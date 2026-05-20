from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.order import Order
from app.models.visitor import TrackingPageVisit
from app.core.config import settings

router = APIRouter(tags=["Tracking"])

@router.get("/track/{tracking_token}", response_class=HTMLResponse)
async def tracking_page(tracking_token: str, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order).where(Order.tracking_token == tracking_token))
    order = result.scalar_one_or_none()

    if not order:
        return HTMLResponse(content=_not_found_html(), status_code=404)

    visit = TrackingPageVisit(
        tracking_token=tracking_token,
        order_id=order.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:200],
    )
    db.add(visit)
    await db.commit()

    return HTMLResponse(content=_tracking_html(tracking_token, order, settings.BASE_URL))


def _status_text(status: str) -> str:
    return {
        "pending":    ("⏳", "Kutilmoqda",        "Buyurtmangiz qabul qilindi"),
        "confirmed":  ("✅", "Tasdiqlandi",        "Restoran buyurtmangizni qabul qildi"),
        "preparing":  ("👨‍🍳", "Tayyorlanmoqda",  "Ovqatingiz tayyorlanmoqda"),
        "picked_up":  ("🛵", "Kuryer oldi",        "Kuryer restorandan oldi"),
        "on_the_way": ("🚀", "Yo'lda",             "Kuryer sizga kelmoqda"),
        "delivered":  ("🎉", "Yetkazildi",         "Ishtaha bo'lsin!"),
        "cancelled":  ("❌", "Bekor qilindi",      "Buyurtma bekor qilindi"),
    }.get(status, ("📦", status, ""))


def _tracking_html(token: str, order, base_url: str) -> str:
    ws_url = base_url.replace("https://", "wss://").replace("http://", "ws://")
    emoji, status_label, status_desc = _status_text(order.status)

    steps = [
        ("pending",    "Buyurtma qabul qilindi", "✓"),
        ("confirmed",  "Restoran tasdiqladi",    "✓"),
        ("preparing",  "Tayyorlanmoqda",         "✓"),
        ("picked_up",  "Kuryer oldi",            "✓"),
        ("on_the_way", "Yo'lda",                 "✓"),
        ("delivered",  "Yetkazildi",             "✓"),
    ]
    order_list = [s[0] for s in steps]
    current_idx = order_list.index(order.status) if order.status in order_list else -1

    steps_html = ""
    for i, (s, label, icon) in enumerate(steps):
        if i < current_idx:
            cls = "done"
        elif i == current_idx:
            cls = "active"
        else:
            cls = ""
        steps_html += f"""
        <div class="step {cls}">
            <div class="step-circle">{icon if i <= current_idx else str(i+1)}</div>
            <div class="step-label">{label}</div>
            {"<div class='step-line'></div>" if i < len(steps)-1 else ""}
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>Buyurtma #{order.id} — PinPoint</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  :root {{
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --gray-50: #f9fafb;
    --gray-100: #f3f4f6;
    --gray-200: #e5e7eb;
    --gray-400: #9ca3af;
    --gray-600: #4b5563;
    --gray-800: #1f2937;
    --shadow: 0 4px 24px rgba(0,0,0,0.08);
    --radius: 16px;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 0 0 40px;
  }}

  /* Header */
  .header {{
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(20px);
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 14px;
    border-bottom: 1px solid rgba(255,255,255,0.2);
  }}
  .header-logo {{
    width: 44px; height: 44px;
    background: white;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  }}
  .header-text h1 {{ color: white; font-size: 17px; font-weight: 700; }}
  .header-text p {{ color: rgba(255,255,255,0.75); font-size: 13px; margin-top: 1px; }}

  /* Container */
  .container {{ padding: 16px; max-width: 480px; margin: 0 auto; }}

  /* Card */
  .card {{
    background: white;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    overflow: hidden;
    margin-bottom: 14px;
  }}

  /* Status card */
  .status-card {{
    padding: 24px;
    text-align: center;
    background: linear-gradient(135deg, #f8f9ff 0%, #fff 100%);
  }}
  .status-emoji {{
    font-size: 52px;
    display: block;
    margin-bottom: 12px;
    animation: pulse 2s infinite;
  }}
  @keyframes pulse {{
    0%, 100% {{ transform: scale(1); }}
    50% {{ transform: scale(1.08); }}
  }}
  .status-label {{
    font-size: 22px;
    font-weight: 700;
    color: var(--gray-800);
    margin-bottom: 6px;
  }}
  .status-desc {{
    font-size: 14px;
    color: var(--gray-400);
  }}
  .eta-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, var(--primary), var(--primary-dark));
    color: white;
    padding: 8px 18px;
    border-radius: 30px;
    font-size: 14px;
    font-weight: 600;
    margin-top: 14px;
    box-shadow: 0 4px 12px rgba(99,102,241,0.35);
  }}

  /* Info card */
  .info-card {{ padding: 20px; }}
  .info-card h3 {{
    font-size: 12px;
    font-weight: 600;
    color: var(--gray-400);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 14px;
  }}
  .info-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid var(--gray-100);
  }}
  .info-row:last-child {{ border-bottom: none; }}
  .info-key {{ font-size: 14px; color: var(--gray-600); }}
  .info-val {{ font-size: 14px; font-weight: 600; color: var(--gray-800); }}
  .price-val {{
    font-size: 16px;
    font-weight: 700;
    color: var(--primary);
  }}

  /* Map */
  #map {{
    height: 240px;
    border-radius: var(--radius);
    overflow: hidden;
    box-shadow: var(--shadow);
    margin-bottom: 14px;
  }}

  /* Steps */
  .steps-card {{ padding: 20px; }}
  .steps-card h3 {{
    font-size: 12px;
    font-weight: 600;
    color: var(--gray-400);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 20px;
  }}
  .steps-container {{
    display: flex;
    justify-content: space-between;
    position: relative;
  }}
  .step {{
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    position: relative;
    z-index: 1;
  }}
  .step-circle {{
    width: 32px; height: 32px;
    border-radius: 50%;
    background: var(--gray-200);
    color: var(--gray-400);
    display: flex; align-items: center; justify-content: center;
    font-size: 12px;
    font-weight: 700;
    transition: all 0.3s;
    position: relative;
    z-index: 2;
  }}
  .step.done .step-circle {{
    background: var(--success);
    color: white;
    box-shadow: 0 2px 8px rgba(16,185,129,0.4);
  }}
  .step.active .step-circle {{
    background: var(--primary);
    color: white;
    box-shadow: 0 2px 12px rgba(99,102,241,0.5);
    animation: stepPulse 1.5s infinite;
  }}
  @keyframes stepPulse {{
    0%, 100% {{ box-shadow: 0 2px 12px rgba(99,102,241,0.5); }}
    50% {{ box-shadow: 0 2px 20px rgba(99,102,241,0.8); }}
  }}
  .step-label {{
    font-size: 10px;
    color: var(--gray-400);
    text-align: center;
    margin-top: 6px;
    max-width: 56px;
    line-height: 1.3;
  }}
  .step.done .step-label, .step.active .step-label {{
    color: var(--gray-800);
    font-weight: 600;
  }}
  .step-line {{
    position: absolute;
    top: 16px;
    left: 50%;
    width: 100%;
    height: 2px;
    background: var(--gray-200);
    z-index: 0;
  }}
  .step.done .step-line {{ background: var(--success); }}

  /* Footer */
  .footer {{
    text-align: center;
    padding: 20px;
    color: rgba(255,255,255,0.6);
    font-size: 12px;
  }}
  .footer span {{ color: rgba(255,255,255,0.9); font-weight: 600; }}

  /* Delivered overlay */
  .delivered-overlay {{
    background: linear-gradient(135deg, #d1fae5, #a7f3d0);
    border-radius: var(--radius);
    padding: 30px;
    text-align: center;
    margin-bottom: 14px;
    box-shadow: var(--shadow);
  }}
  .delivered-overlay .big-emoji {{ font-size: 64px; }}
  .delivered-overlay h2 {{ font-size: 22px; font-weight: 700; color: #065f46; margin: 12px 0 6px; }}
  .delivered-overlay p {{ color: #047857; font-size: 15px; }}

  /* Live dot */
  .live-dot {{
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(16,185,129,0.1);
    color: var(--success);
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin-top: 8px;
  }}
  .live-dot::before {{
    content: '';
    width: 7px; height: 7px;
    background: var(--success);
    border-radius: 50%;
    animation: blink 1s infinite;
  }}
  @keyframes blink {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.3; }}
  }}
</style>
</head>
<body>

<div class="header">
  <div class="header-logo">📍</div>
  <div class="header-text">
    <h1>PinPoint Delivery</h1>
    <p>Buyurtma #{order.id} kuzatuvi</p>
  </div>
</div>

<div class="container">

  <!-- Status -->
  <div class="card">
    <div class="status-card">
      <span class="status-emoji" id="status-emoji">{emoji}</span>
      <div class="status-label" id="status-label">{status_label}</div>
      <div class="status-desc" id="status-desc">{status_desc}</div>
      <div id="eta-block" style="display:none">
        <div class="eta-badge">⏱ <span id="eta-text"></span></div>
      </div>
      <div class="live-dot" id="live-dot">Jonli kuzatuv</div>
    </div>
  </div>

  <!-- Map -->
  <div id="map"></div>

  <!-- Steps -->
  <div class="card">
    <div class="steps-card">
      <h3>Yetkazib berish bosqichlari</h3>
      <div class="steps-container" id="steps-container">
        {steps_html}
      </div>
    </div>
  </div>

  <!-- Info -->
  <div class="card">
    <div class="info-card">
      <h3>Buyurtma ma'lumotlari</h3>
      <div class="info-row">
        <span class="info-key">📍 Manzil</span>
        <span class="info-val" style="max-width:180px;text-align:right;font-size:13px">{order.delivery_address}</span>
      </div>
      <div class="info-row">
        <span class="info-key">💰 Ovqat narxi</span>
        <span class="info-val">{order.items_price:,.0f} so'm</span>
      </div>
      <div class="info-row">
        <span class="info-key">🛵 Yetkazish</span>
        <span class="info-val">{order.delivery_fee:,.0f} so'm</span>
      </div>
      <div class="info-row">
        <span class="info-key">💳 Jami</span>
        <span class="price-val">{order.total_price:,.0f} so'm</span>
      </div>
    </div>
  </div>

</div>

<div class="footer">
  Powered by <span>PinPoint</span> — Tez va ishonchli yetkazib berish
</div>

<script>
const TOKEN = "{token}";
const WS_URL = "{ws_url}/api/v1/delivery/guest/ws/" + TOKEN;
const DEST_LAT = {order.delivery_lat};
const DEST_LON = {order.delivery_lon};

// Xarita
const map = L.map('map', {{zoomControl: false}}).setView([DEST_LAT, DEST_LON], 15);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
L.control.zoom({{position: 'bottomright'}}).addTo(map);

const destMarker = L.marker([DEST_LAT, DEST_LON], {{
  icon: L.divIcon({{
    html: '<div style="background:#6366f1;color:white;border-radius:50%;width:36px;height:36px;display:flex;align-items:center;justify-content:center;font-size:18px;box-shadow:0 2px 8px rgba(99,102,241,0.5)">📍</div>',
    className: '', iconSize: [36,36], iconAnchor: [18,36]
  }})
}}).addTo(map).bindPopup('<b>Yetkazib berish manzili</b>');

let courierMarker = null;
let routeLine = null;

const STATUS_DATA = {{
  pending:    ['⏳', 'Kutilmoqda',       'Buyurtmangiz qabul qilindi'],
  confirmed:  ['✅', 'Tasdiqlandi',      'Restoran buyurtmangizni qabul qildi'],
  preparing:  ['👨‍🍳','Tayyorlanmoqda', 'Ovqatingiz tayyorlanmoqda'],
  picked_up:  ['🛵', 'Kuryer oldi',      'Kuryer restorandan oldi'],
  on_the_way: ['🚀', 'Yo\'lda',          'Kuryer sizga kelmoqda'],
  delivered:  ['🎉', 'Yetkazildi',       'Ishtaha bo\'lsin!'],
  cancelled:  ['❌', 'Bekor qilindi',    'Buyurtma bekor qilindi'],
}};

const STEP_ORDER = ['pending','confirmed','preparing','picked_up','on_the_way','delivered'];
const STEP_LABELS = ['Qabul qilindi','Tasdiqlandi','Tayyorlanmoqda','Kuryer oldi','Yo\'lda','Yetkazildi'];

function updateStatus(status) {{
  const d = STATUS_DATA[status] || ['📦', status, ''];
  document.getElementById('status-emoji').textContent = d[0];
  document.getElementById('status-label').textContent = d[1];
  document.getElementById('status-desc').textContent = d[2];

  const idx = STEP_ORDER.indexOf(status);
  let html = '';
  STEP_ORDER.forEach((s, i) => {{
    const cls = i < idx ? 'done' : i === idx ? 'active' : '';
    const circle = i <= idx ? '✓' : (i+1);
    const line = i < STEP_ORDER.length-1 ? "<div class='step-line'></div>" : '';
    html += `<div class="step ${{cls}}"><div class="step-circle">${{circle}}</div><div class="step-label">${{STEP_LABELS[i]}}</div>${{line}}</div>`;
  }});
  document.getElementById('steps-container').innerHTML = html;

  if (status === 'delivered') {{
    document.getElementById('live-dot').style.display = 'none';
  }}
  if (status === 'cancelled') {{
    document.getElementById('live-dot').style.display = 'none';
    document.getElementById('live-dot').textContent = 'Bekor qilindi';
  }}
}}

function connect() {{
  const ws = new WebSocket(WS_URL);

  ws.onopen = () => {{
    document.getElementById('live-dot').style.display = 'inline-flex';
  }};

  ws.onmessage = (e) => {{
    const data = JSON.parse(e.data);
    if (data.status) updateStatus(data.status);

    if (data.courier_location) {{
      const lat = data.courier_location.lat;
      const lon = data.courier_location.lon;
      if (courierMarker) {{
        courierMarker.setLatLng([lat, lon]);
      }} else {{
        courierMarker = L.marker([lat, lon], {{
          icon: L.divIcon({{
            html: '<div style="background:#10b981;color:white;border-radius:50%;width:40px;height:40px;display:flex;align-items:center;justify-content:center;font-size:20px;box-shadow:0 2px 10px rgba(16,185,129,0.5);animation:pulse 1.5s infinite">🛵</div>',
            className: '', iconSize: [40,40], iconAnchor: [20,20]
          }})
        }}).addTo(map).bindPopup('<b>Kuryer</b>');
      }}

      // Kuryer va manzil orasida chiziq
      if (routeLine) map.removeLayer(routeLine);
      routeLine = L.polyline([[lat, lon], [DEST_LAT, DEST_LON]], {{
        color: '#6366f1', weight: 3, opacity: 0.6, dashArray: '8,6'
      }}).addTo(map);

      map.fitBounds([[lat, lon], [DEST_LAT, DEST_LON]], {{padding: [40, 40]}});
    }}

    if (data.estimated_minutes) {{
      document.getElementById('eta-block').style.display = 'block';
      document.getElementById('eta-text').textContent = data.estimated_minutes + ' daqiqada yetadi';
    }}
  }};

  ws.onclose = () => {{
    document.getElementById('live-dot').style.display = 'none';
    setTimeout(connect, 4000);
  }};
}}

connect();
</script>
</body>
</html>"""


def _not_found_html() -> str:
    return """<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Topilmadi — PinPoint</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  body { font-family:'Inter',sans-serif; background:linear-gradient(135deg,#667eea,#764ba2); min-height:100vh; display:flex; align-items:center; justify-content:center; }
  .box { background:white; border-radius:20px; padding:48px 40px; text-align:center; box-shadow:0 20px 60px rgba(0,0,0,0.15); max-width:360px; }
  .emoji { font-size:64px; margin-bottom:16px; }
  h2 { font-size:22px; font-weight:700; color:#1f2937; margin-bottom:8px; }
  p { color:#9ca3af; font-size:15px; line-height:1.5; }
</style>
</head>
<body>
  <div class="box">
    <div class="emoji">😕</div>
    <h2>Buyurtma topilmadi</h2>
    <p>Link noto'g'ri yoki muddati o'tgan bo'lishi mumkin</p>
  </div>
</body>
</html>"""
