#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import os

OUT = os.path.join(os.path.dirname(__file__), '..', 'overview.png')
W, H = 1280, 820
img = Image.new('RGB', (W, H), color='white')
d = ImageDraw.Draw(img)

# Fonts
try:
    font_title = ImageFont.truetype('Arial.ttf', 18)
    font_sub = ImageFont.truetype('Arial.ttf', 12)
    font_box_title = ImageFont.truetype('Arial.ttf', 14)
    font_box_text = ImageFont.truetype('Arial.ttf', 12)
except Exception:
    font_title = ImageFont.load_default()
    font_sub = ImageFont.load_default()
    font_box_title = ImageFont.load_default()
    font_box_text = ImageFont.load_default()

# Title Banner
d.rectangle([(20,20),(1260,100)], fill=(43,101,236), outline=None)
text = "AI Ecosystem — WTN-A09: Observability Architecture Diagram"
bbox = d.textbbox((0,0), text, font=font_title)
w = bbox[2] - bbox[0]
d.text(((W-w)/2, 35), text, font=font_title, fill='white')
sub = "Distributed Tracing (Tempo), Time-Series Metrics (Prometheus), Log Aggregation (Loki), OTel Collector & Grafana UI"
bbox2 = d.textbbox((0,0), sub, font=font_sub)
w2 = bbox2[2] - bbox2[0]
d.text(((W-w2)/2, 60), sub, font=font_sub, fill='white')

def draw_box(x, y, w, h, color, title, lines):
    d.rectangle([(x,y),(x+w,y+h)], fill=color, outline='black')
    d.text((x+10, y+10), title, font=font_box_title, fill='white')
    ty = y+36
    for line in lines:
        d.text((x+10, ty), line, font=font_box_text, fill='white')
        ty += 18

# Left column
draw_box(20,120,260,120,(59,130,246),'FastAPI Web API',["Port: 8000","OTLP Traces & Metrics","Prometheus: /metrics","Structured JSON Logs"]) 

draw_box(20,260,260,120,(124,58,237),'Inference Worker',["Redis Queue Daemon","OTLP Spans & Metrics","Token Classification","Structured Logs"]) 

draw_box(20,400,260,120,(124,58,237),'Trainer Worker',["Fine-tuning Daemon","PyTorch Model Training","MLflow Logging","Telemetry Events"]) 

# Collector
draw_box(320,200,300,220,(249,115,22),'OpenTelemetry Collector',["OTel Collector Contrib","Receiver: OTLP gRPC 4317","Receiver: OTLP HTTP 4318","Processors: Batch, Memory","Health: 13133","Exporter: Prometheus 8889","Exporter: Tempo & Loki"]) 

# Backends
draw_box(650,120,260,120,(220,38,38),'Prometheus Engine',["Port: 9090","Scrapes /metrics & 8889","TSDB Storage","AlertManager & PromQL"]) 

draw_box(650,260,260,120,(22,163,74),'Grafana Loki Engine',["Port: 3100","Centralized Log Index","LogQL Query Language","Chunk Store (Filesystem)"]) 

draw_box(650,400,260,120,(244,114,182),'Grafana Tempo Engine',["Port: 3200","Distributed Tracing","OTLP Traces Receiver","Span & Block Storage"]) 

# Grafana UI
draw_box(980,200,260,220,(14,165,164),'Grafana UI Platform',["Port: 3000","Unified Dashboard","Prometheus Metrics","Loki Log Explorer","Tempo Trace Viewer","Unified Alerting"]) 

# Arrows (simple lines)
# FastAPI -> Collector
d.line([(280,180),(320,240)], fill='black', width=3)
d.text((300,200),'OTLP HTTP', fill='black', font=font_box_text)
# Inference -> Collector
d.line([(280,320),(320,300)], fill='black', width=3)
d.text((300,310),'OTLP HTTP', fill='black', font=font_box_text)
# Trainer -> Collector
d.line([(280,460),(320,360)], fill='black', width=3)
d.text((300,410),'OTLP HTTP', fill='black', font=font_box_text)
# Collector -> Prometheus
d.line([(620,300),(650,180)], fill=(185,28,28), width=3)
d.text((620,250),'Metrics (8889)', fill='black', font=font_box_text)
# Collector -> Loki
d.line([(620,320),(650,320)], fill=(21,128,61), width=3)
d.text((620,335),'OTLP Logs', fill='black', font=font_box_text)
# Collector -> Tempo
d.line([(620,340),(650,420)], fill=(190,24,93), width=3)
d.text((620,370),'OTLP Traces', fill='black', font=font_box_text)
# Prometheus -> Grafana
d.line([(910,180),(980,260)], fill='black', width=3)
d.text((940,200),'PromQL', fill='black', font=font_box_text)
# Loki -> Grafana
d.line([(910,320),(980,280)], fill='black', width=3)
d.text((940,300),'LogQL', fill='black', font=font_box_text)
# Tempo -> Grafana
d.line([(910,420),(980,320)], fill='black', width=3)
d.text((940,360),'Trace Search', fill='black', font=font_box_text)

img.save(OUT)
print('Wrote', OUT)
