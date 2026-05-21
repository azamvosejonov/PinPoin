from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.order import Order, OrderItem
from app.models.restaurant import Restaurant, MenuItem
from app.models.visitor import TrackingPageVisit
from app.core.config import settings

router = APIRouter(tags=["Tracking"])

@router.get("/track/{tracking_token}", response_class=HTMLResponse)
async def tracking_page(tracking_token: str, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order).where(Order.tracking_token == tracking_token))
    order = result.scalar_one_or_none()
    if not order:
        return HTMLResponse(content=_not_found_html(), status_code=404)

    rest_result = await db.execute(select(Restaurant).where(Restaurant.id == order.restaurant_id))
    restaurant = rest_result.scalar_one_or_none()

    temp_warning = False
    food_names = []
    if order.ai_analysis:
        temp_warning = order.ai_analysis.get("temperature_warning", False)

    items_result = await db.execute(select(OrderItem).where(OrderItem.order_id == order.id))
    for item in items_result.scalars().all():
        if item.menu_item_id:
            m = await db.execute(select(MenuItem).where(MenuItem.id == item.menu_item_id))
            mi = m.scalar_one_or_none()
            if mi:
                food_names.append(f"{mi.name} ×{item.quantity}")
                if mi.temperature_sensitive:
                    temp_warning = True

    visit = TrackingPageVisit(
        tracking_token=tracking_token,
        order_id=order.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:200],
    )
    db.add(visit)
    await db.commit()

    return HTMLResponse(content=_build(
        token=tracking_token,
        order=order,
        restaurant=restaurant,
        food_names=food_names,
        temp_warning=temp_warning,
        base_url=settings.BASE_URL,
    ))


def _build(token, order, restaurant, food_names, temp_warning, base_url):
    ws = base_url.replace("https://", "wss://").replace("http://", "ws://")
    rest_name = restaurant.name if restaurant else "Restoran"
    food_str = " · ".join(food_names) if food_names else ""

    ST = {
        "pending":    ("⏳", "Kutilmoqda",       "#f59e0b", "rgba(245,158,11,0.15)"),
        "confirmed":  ("✅", "Tasdiqlandi",       "#10b981", "rgba(16,185,129,0.15)"),
        "preparing":  ("👨🍳","Tayyorlanmoqda",  "#8b5cf6", "rgba(139,92,246,0.15)"),
        "picked_up":  ("🛵", "Kuryer oldi",       "#3b82f6", "rgba(59,130,246,0.15)"),
        "on_the_way": ("🚀", "Yo'lda",            "#6366f1", "rgba(99,102,241,0.15)"),
        "delivered":  ("🎉", "Yetkazildi",        "#10b981", "rgba(16,185,129,0.15)"),
        "cancelled":  ("❌", "Bekor qilindi",     "#ef4444", "rgba(239,68,68,0.15)"),
    }
    emoji, slabel, scolor, sbg = ST.get(order.status, ("📦", order.status, "#6366f1", "rgba(99,102,241,0.15)"))

    return f"""<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>{rest_name} — Kuzatuv</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}}
html,body{{width:100%;height:100%;overflow:hidden;font-family:'Inter',sans-serif;background:#0d0d1a}}

/* ── XARITA TO'LIQ EKRAN ── */
#map{{
  position:fixed;inset:0;z-index:1;
  width:100%;height:100%;
}}

/* ── RAIN ── */
#rain{{position:fixed;inset:0;z-index:2;pointer-events:none}}

/* ── HEADER ── */
.hdr{{
  position:fixed;top:0;left:0;right:0;z-index:100;
  display:flex;align-items:center;gap:10px;
  padding:12px 16px;
  background:linear-gradient(180deg,rgba(13,13,26,0.95) 0%,rgba(13,13,26,0.7) 100%);
  backdrop-filter:blur(20px);
  border-bottom:1px solid rgba(255,255,255,0.06);
}}
.logo{{
  width:36px;height:36px;flex-shrink:0;
  background:linear-gradient(135deg,#6366f1,#8b5cf6);
  border-radius:10px;
  display:flex;align-items:center;justify-content:center;
  font-size:16px;
  box-shadow:0 4px 14px rgba(99,102,241,0.5);
}}
.hdr-info{{flex:1;min-width:0}}
.hdr-info h1{{font-size:13px;font-weight:700;color:#f1f5f9;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.hdr-info p{{font-size:10px;color:rgba(255,255,255,0.4);margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.live{{
  flex-shrink:0;
  display:flex;align-items:center;gap:4px;
  background:rgba(16,185,129,0.12);
  border:1px solid rgba(16,185,129,0.25);
  color:#10b981;
  padding:4px 9px;border-radius:20px;
  font-size:10px;font-weight:700;letter-spacing:0.3px;
}}
.ld{{width:5px;height:5px;background:#10b981;border-radius:50%;animation:blink 1.2s infinite}}
@keyframes blink{{0%,100%{{opacity:1;box-shadow:0 0 5px #10b981}}50%{{opacity:0.1;box-shadow:none}}}}

/* ── BOTTOM PANEL ── */
.panel{{
  position:fixed;bottom:0;left:0;right:0;z-index:100;
  background:linear-gradient(0deg,rgba(13,13,26,0.98) 0%,rgba(13,13,26,0.92) 100%);
  backdrop-filter:blur(30px);
  border-top:1px solid rgba(255,255,255,0.07);
  border-radius:24px 24px 0 0;
  padding:8px 16px 32px;
  transition:transform .4s cubic-bezier(.32,1,.32,1);
}}
.drag-bar{{
  width:36px;height:4px;
  background:rgba(255,255,255,0.15);
  border-radius:2px;
  margin:0 auto 14px;
}}

/* STATUS */
.status-row{{
  display:flex;align-items:center;gap:12px;
  padding:12px 14px;
  background:{sbg};
  border:1px solid {scolor}33;
  border-radius:16px;
  margin-bottom:10px;
}}
.s-em{{font-size:32px;flex-shrink:0;animation:bob 2.5s ease-in-out infinite}}
@keyframes bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-4px)}}}}
.s-label{{font-size:17px;font-weight:800;color:{scolor};letter-spacing:-0.3px}}
.s-desc{{font-size:11px;color:rgba(255,255,255,0.45);margin-top:2px;line-height:1.4}}

/* ETA + DIST ROW */
.metrics{{display:flex;gap:8px;margin-bottom:10px}}
.metric{{
  flex:1;
  background:rgba(255,255,255,0.05);
  border:1px solid rgba(255,255,255,0.08);
  border-radius:14px;
  padding:12px 10px;
  text-align:center;
}}
.metric-val{{font-size:18px;font-weight:800;color:#f1f5f9;letter-spacing:-0.5px}}
.metric-label{{font-size:9px;color:rgba(255,255,255,0.35);text-transform:uppercase;letter-spacing:0.8px;margin-top:3px;font-weight:600}}
.metric.eta-m .metric-val{{color:#a5b4fc}}
.metric.dist-m .metric-val{{color:#6ee7b7}}
.metric.arr-m .metric-val{{color:#fcd34d}}

/* TEMP */
.temp{{
  display:flex;align-items:center;gap:10px;
  padding:10px 14px;
  background:rgba(239,68,68,0.08);
  border:1px solid rgba(239,68,68,0.2);
  border-radius:14px;
  margin-bottom:10px;
  animation:tpulse 2s ease-in-out infinite;
}}
@keyframes tpulse{{0%,100%{{border-color:rgba(239,68,68,0.2)}}50%{{border-color:rgba(239,68,68,0.5)}}}}
.temp-em{{font-size:22px;flex-shrink:0}}
.temp-t{{font-size:12px;font-weight:700;color:#fca5a5}}
.temp-s{{font-size:10px;color:rgba(255,255,255,0.4);margin-top:1px}}
.temp-badge{{
  margin-left:auto;flex-shrink:0;
  background:rgba(239,68,68,0.2);
  border:1px solid rgba(239,68,68,0.3);
  color:#fca5a5;
  padding:3px 8px;border-radius:20px;
  font-size:9px;font-weight:800;letter-spacing:0.5px;
}}

/* FOOD */
.food{{
  display:flex;align-items:center;gap:8px;
  padding:9px 14px;
  background:rgba(255,255,255,0.04);
  border:1px solid rgba(255,255,255,0.07);
  border-radius:12px;
}}
.food-em{{font-size:18px;flex-shrink:0}}
.food-t{{font-size:12px;color:rgba(255,255,255,0.5);line-height:1.4}}

/* MAP ZOOM CONTROLS */
.leaflet-control-zoom{{
  border:none!important;
  box-shadow:0 4px 20px rgba(0,0,0,0.5)!important;
  border-radius:12px!important;
  overflow:hidden;
}}
.leaflet-control-zoom a{{
  background:rgba(13,13,26,0.92)!important;
  color:#f1f5f9!important;
  border:none!important;
  border-bottom:1px solid rgba(255,255,255,0.08)!important;
  width:36px!important;height:36px!important;
  line-height:36px!important;
  font-size:18px!important;
  backdrop-filter:blur(10px);
}}
.leaflet-control-zoom a:last-child{{border-bottom:none!important}}
.leaflet-control-zoom a:hover{{background:rgba(99,102,241,0.3)!important}}

/* POPUP */
.leaflet-popup-content-wrapper{{
  background:rgba(13,13,26,0.97)!important;
  color:#f1f5f9!important;
  border:1px solid rgba(255,255,255,0.1)!important;
  border-radius:14px!important;
  box-shadow:0 8px 32px rgba(0,0,0,0.6)!important;
  padding:0!important;
}}
.leaflet-popup-content{{margin:12px 16px!important;font-family:'Inter',sans-serif!important;font-size:13px!important;font-weight:600!important}}
.leaflet-popup-tip{{background:rgba(13,13,26,0.97)!important}}
.leaflet-popup-close-button{{color:rgba(255,255,255,0.4)!important;font-size:18px!important;top:6px!important;right:8px!important}}

/* TILES */
.leaflet-tile{{filter:brightness(0.85) saturate(0.9) contrast(1.05)}}

/* ATTRIBUTION */
.leaflet-control-attribution{{
  background:rgba(13,13,26,0.7)!important;
  color:rgba(255,255,255,0.3)!important;
  font-size:9px!important;
  border-radius:6px 0 0 0!important;
  padding:2px 6px!important;
}}
.leaflet-control-attribution a{{color:rgba(255,255,255,0.4)!important}}

/* PULSE RING on destination */
@keyframes ring{{
  0%{{transform:scale(1);opacity:0.6}}
  100%{{transform:scale(3);opacity:0}}
}}
</style>
</head>
<body>

<canvas id="rain"></canvas>

<!-- Header -->
<div class="hdr">
  <div class="logo">📍</div>
  <div class="hdr-info">
    <h1>{rest_name}</h1>
    <p>Buyurtma #{order.id} · {order.delivery_address}</p>
  </div>
  <div class="live" id="live"><div class="ld"></div>JONLI</div>
</div>

<!-- Map -->
<div id="map"></div>

<!-- Bottom panel -->
<div class="panel" id="panel">
  <div class="drag-bar"></div>

  <!-- Status -->
  <div class="status-row">
    <div class="s-em" id="se">{emoji}</div>
    <div>
      <div class="s-label" id="sl">{slabel}</div>
      <div class="s-desc" id="sd">Kuzatilmoqda...</div>
    </div>
  </div>

  <!-- Metrics -->
  <div class="metrics" id="metrics" style="display:none">
    <div class="metric eta-m">
      <div class="metric-val" id="mv-eta">—</div>
      <div class="metric-label">Vaqt</div>
    </div>
    <div class="metric dist-m">
      <div class="metric-val" id="mv-dist">—</div>
      <div class="metric-label">Masofa</div>
    </div>
    <div class="metric arr-m">
      <div class="metric-val" id="mv-arr">—</div>
      <div class="metric-label">Yetib kelish</div>
    </div>
  </div>

  <!-- Temp warning -->
  {"" if not temp_warning else """
  <div class="temp">
    <div class="temp-em">🌡️</div>
    <div>
      <div class="temp-t">Issiq ovqat — tez yetkazilishi kerak</div>
      <div class="temp-s">Ovqat sovib qolmasligi uchun kuryer tezlashtirilgan</div>
    </div>
    <div class="temp-badge">ISSIQ</div>
  </div>"""}

  <!-- Food -->
  {"" if not food_str else f'<div class="food"><div class="food-em">🍽</div><div class="food-t">{food_str}</div></div>'}

</div>

<script>
/* ── Rain ── */
(function(){{
  var c=document.getElementById('rain'),x=c.getContext('2d'),D=[];
  function R(){{c.width=innerWidth;c.height=innerHeight}}R();
  addEventListener('resize',R);
  for(var i=0;i<180;i++)D.push({{
    x:Math.random()*innerWidth,y:Math.random()*innerHeight,
    l:Math.random()*20+8,s:Math.random()*4+2,
    o:Math.random()*0.18+0.03
  }});
  (function draw(){{
    x.clearRect(0,0,c.width,c.height);
    D.forEach(function(d){{
      x.beginPath();x.moveTo(d.x,d.y);
      x.lineTo(d.x-d.l*0.18,d.y+d.l);
      x.strokeStyle='rgba(148,163,184,'+d.o+')';
      x.lineWidth=0.65;x.stroke();
      d.y+=d.s;d.x-=d.s*0.18;
      if(d.y>c.height){{d.y=-25;d.x=Math.random()*c.width}}
    }});
    requestAnimationFrame(draw);
  }})();
}})();

/* ── Map ── */
var DL={order.delivery_lat},DN={order.delivery_lon};
var PANEL_H=document.getElementById('panel').offsetHeight;

var map=L.map('map',{{
  zoomControl:false,
  attributionControl:true,
  paddingBottomRight:[0,PANEL_H+20]
}}).setView([DL,DN],15);

L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png',{{
  attribution:'© <a href="https://carto.com">CARTO</a>',
  maxZoom:19
}}).addTo(map);

L.control.zoom({{position:'topright'}}).addTo(map);

/* Destination marker */
var destIcon=L.divIcon({{
  html:`<div style="position:relative;width:52px;height:60px">
    <div style="position:absolute;bottom:0;left:50%;transform:translateX(-50%);
      width:52px;height:52px;
      background:linear-gradient(135deg,#6366f1,#8b5cf6);
      border-radius:50% 50% 50% 4px;
      transform:translateX(-50%) rotate(-45deg);
      box-shadow:0 8px 28px rgba(99,102,241,0.7);
      border:2.5px solid rgba(255,255,255,0.3);
      display:flex;align-items:center;justify-content:center">
      <span style="transform:rotate(45deg);font-size:22px;display:block">🏠</span>
    </div>
  </div>`,
  className:'',iconSize:[52,60],iconAnchor:[26,60]
}});
var destMarker=L.marker([DL,DN],{{icon:destIcon}}).addTo(map);
destMarker.bindPopup('<div style="font-weight:700;font-size:13px">📍 Yetkazib berish manzili</div>');

/* Pulse ring on destination */
var pulseIcon=L.divIcon({{
  html:`<div style="width:80px;height:80px;border-radius:50%;
    border:2px solid rgba(99,102,241,0.4);
    animation:ring 2s ease-out infinite;
    position:absolute;top:50%;left:50%;
    transform:translate(-50%,-50%)"></div>`,
  className:'',iconSize:[80,80],iconAnchor:[40,40]
}});
L.marker([DL,DN],{{icon:pulseIcon,interactive:false,zIndexOffset:-100}}).addTo(map);

var cMarker=null,routeLine=null;
var prevLat=null,prevLon=null,prevTime=null;

/* Status */
var SD={{
  pending:   ['⏳','Kutilmoqda','Buyurtmangiz restoranda qabul qilindi'],
  confirmed: ['✅','Tasdiqlandi','Restoran buyurtmangizni tasdiqlamoqda'],
  preparing: ['👨🍳','Tayyorlanmoqda','Oshpaz ovqatingizni tayyorlamoqda'],
  picked_up: ['🛵','Kuryer oldi','Kuryer restorandan ovqatni oldi'],
  on_the_way:['🚀',"Yo'lda",'Kuryer sizga tomon kelmoqda'],
  delivered: ['🎉','Yetkazildi',"Ovqatingiz yetkazildi. Ishtaha bo'lsin!"],
  cancelled: ['❌','Bekor qilindi','Buyurtma bekor qilindi']
}};

function setStatus(s){{
  var d=SD[s]||['📦',s,''];
  document.getElementById('se').textContent=d[0];
  document.getElementById('sl').textContent=d[1];
  document.getElementById('sd').textContent=d[2];
  if(s==='delivered'||s==='cancelled')
    document.getElementById('live').style.display='none';
}}

function haversine(la1,lo1,la2,lo2){{
  var R=6371,r=Math.PI/180;
  var dLa=(la2-la1)*r,dLo=(lo2-lo1)*r;
  var a=Math.sin(dLa/2)*Math.sin(dLa/2)+
        Math.cos(la1*r)*Math.cos(la2*r)*
        Math.sin(dLo/2)*Math.sin(dLo/2);
  return R*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));
}}

function pad(n){{return n.toString().padStart(2,'0')}}

function updateCourier(lat,lon){{
  /* Courier marker */
  var ci=L.divIcon({{
    html:`<div style="position:relative;width:54px;height:62px">
      <div style="position:absolute;bottom:0;left:50%;transform:translateX(-50%);
        width:54px;height:54px;
        background:linear-gradient(135deg,#10b981,#059669);
        border-radius:50%;
        box-shadow:0 8px 28px rgba(16,185,129,0.7);
        border:2.5px solid rgba(255,255,255,0.3);
        display:flex;align-items:center;justify-content:center;
        font-size:26px">🛵</div>
      <div style="position:absolute;bottom:-10px;left:50%;transform:translateX(-50%);
        background:rgba(16,185,129,0.9);color:#fff;
        font-size:9px;font-weight:800;padding:2px 7px;
        border-radius:8px;white-space:nowrap;
        font-family:Inter,sans-serif;letter-spacing:0.3px">KURYER</div>
    </div>`,
    className:'',iconSize:[54,72],iconAnchor:[27,72]
  }});

  if(cMarker) cMarker.setLatLng([lat,lon]);
  else cMarker=L.marker([lat,lon],{{icon:ci,zIndexOffset:1000}}).addTo(map);

  /* Route */
  if(routeLine) map.removeLayer(routeLine);
  routeLine=L.polyline([[lat,lon],[DL,DN]],{{
    color:'#6366f1',weight:3,opacity:0.75,
    dashArray:'12,8',lineCap:'round',lineJoin:'round'
  }}).addTo(map);

  /* Fit with panel offset */
  var ph=document.getElementById('panel').offsetHeight;
  map.fitBounds([[lat,lon],[DL,DN]],{{
    paddingTopLeft:[60,80],
    paddingBottomRight:[60,ph+40],
    maxZoom:16,animate:true,duration:0.8
  }});

  /* Distance & speed */
  var dist=haversine(lat,lon,DL,DN);
  var now=Date.now(),speed=null;
  if(prevLat!==null){{
    var moved=haversine(prevLat,prevLon,lat,lon);
    var dt=(now-prevTime)/3600000;
    if(dt>0.0001&&moved>0.001) speed=moved/dt;
  }}
  prevLat=lat;prevLon=lon;prevTime=now;

  document.getElementById('metrics').style.display='flex';
  document.getElementById('mv-dist').textContent=
    dist<1?(Math.round(dist*1000)+'m'):(dist.toFixed(1)+'km');

  if(speed&&speed>0.5){{
    var mins=Math.round((dist/speed)*60);
    document.getElementById('mv-eta').textContent=mins+'min';
    var arr=new Date(Date.now()+mins*60000);
    document.getElementById('mv-arr').textContent=pad(arr.getHours())+':'+pad(arr.getMinutes());
  }}
}}

/* WebSocket */
function conn(){{
  var ws=new WebSocket('{ws}/api/v1/delivery/guest/ws/{token}');
  ws.onopen=function(){{document.getElementById('live').style.display='flex'}};
  ws.onmessage=function(e){{
    var d=JSON.parse(e.data);
    if(d.status) setStatus(d.status);
    if(d.courier_location) updateCourier(d.courier_location.lat,d.courier_location.lon);
    if(d.estimated_minutes){{
      var m=d.estimated_minutes;
      document.getElementById('metrics').style.display='flex';
      document.getElementById('mv-eta').textContent=m+'min';
      var arr=new Date(Date.now()+m*60000);
      document.getElementById('mv-arr').textContent=pad(arr.getHours())+':'+pad(arr.getMinutes());
    }}
  }};
  ws.onclose=function(){{
    document.getElementById('live').style.display='none';
    setTimeout(conn,4000);
  }};
}}
conn();

/* Panel drag (swipe up/down) */
(function(){{
  var panel=document.getElementById('panel');
  var startY,startH,dragging=false;
  var minH=120,maxH=Math.round(innerHeight*0.65);

  panel.addEventListener('touchstart',function(e){{
    startY=e.touches[0].clientY;
    startH=panel.offsetHeight;
    dragging=true;
  }},{{passive:true}});
  document.addEventListener('touchmove',function(e){{
    if(!dragging) return;
    var dy=startY-e.touches[0].clientY;
    var nh=Math.max(minH,Math.min(maxH,startH+dy));
    panel.style.height=nh+'px';
  }},{{passive:true}});
  document.addEventListener('touchend',function(){{dragging=false}});
}})();
</script>
</body>
</html>"""


def _not_found_html() -> str:
    return """<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Topilmadi — PinPoint</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',sans-serif;background:#0d0d1a;min-height:100vh;display:flex;align-items:center;justify-content:center}
.bg{position:fixed;inset:0;background:radial-gradient(ellipse 70% 50% at 20% 20%,rgba(99,102,241,0.1),transparent),#0d0d1a}
.box{position:relative;z-index:1;background:rgba(255,255,255,0.05);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,0.08);border-radius:24px;padding:48px 40px;text-align:center;max-width:360px;width:90%;box-shadow:0 20px 60px rgba(0,0,0,0.5)}
.em{font-size:64px;display:block;margin-bottom:18px;animation:f 3s ease-in-out infinite}
@keyframes f{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
h2{font-size:22px;font-weight:800;color:#f1f5f9;margin-bottom:8px}
p{color:#64748b;font-size:14px;line-height:1.6}
</style>
</head>
<body>
<div class="bg"></div>
<div class="box">
  <span class="em">😕</span>
  <h2>Buyurtma topilmadi</h2>
  <p>Link noto'g'ri yoki muddati o'tgan bo'lishi mumkin</p>
</div>
</body>
</html>"""
