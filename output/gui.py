# output/gui.py — NEXUS HUD v6 (Siri-style mini + Iron Man full)
import tkinter as tk
import math, time, psutil, random, colorsys
from datetime import datetime

BG    = "#000408"
WHITE = "#ffffff"

class NexusHUD:
    def __init__(self):
        self.root = tk.Tk()
        self.root.configure(bg=BG)
        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()
        self.cx = self.sw // 2
        self.cy = self.sh // 2
        self.root.geometry(f"{self.sw}x{self.sh}+0+0")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.0)

        self.state        = "idle"
        self.alpha        = 0.0
        self.visible      = False
        self.mode         = "full"
        self.tick         = 0
        self.breath       = 0.0
        self.conversation = []
        self.full_text    = ""
        self.shown_text   = ""
        self.char_idx     = 0

        # Full screen VFX
        self.radar_angle     = 0.0
        self.radar_trail     = []
        self.particles       = []
        self.lightning       = []
        self.lightning_timer = 0
        self.columns         = []
        self.rings           = []
        self.glitch_timer    = 0
        self.glitch_on       = False
        self.orbs            = []
        self.vwave           = [0.0] * 100
        self.scan_lines      = []
        self.energy_pool     = 1.0

        # Mini Siri-style VFX
        self.siri_blobs      = []   # organic color blobs
        self.siri_wave       = [0.0] * 60
        self.siri_phase      = 0.0
        self.siri_ripples    = []

        self._init_columns()
        self._init_orbs()
        self._init_scan_lines()
        self._init_siri_blobs()

        self.canvas = tk.Canvas(self.root,
            width=self.sw, height=self.sh,
            bg=BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.canvas.bind("<Button-1>", lambda e: self._toggle_mode())
        self._start_loops()

    # ── COLOR ENGINE ─────────────────────────────────────────────
    def _hue(self):
        return {"idle":0.53,"listening":0.36,
                "thinking":0.07,"speaking":0.58}.get(self.state, 0.53)

    def _rgb(self, h, s, l):
        r,g,b = colorsys.hls_to_rgb(h%1.0, l, s)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

    def _c(self, l=0.7, s=1.0):
        return self._rgb(self._hue(), s, l)

    def _c2(self, hue, l=0.7, s=1.0):
        return self._rgb(hue, s, l)

    def _dim(self, col, f):
        try:
            r=int(col[1:3],16); g=int(col[3:5],16); b=int(col[5:7],16)
            return f"#{max(0,int(r*(1-f))):02x}{max(0,int(g*(1-f))):02x}{max(0,int(b*(1-f))):02x}"
        except: return col

    # ── INIT SYSTEMS ─────────────────────────────────────────────
    def _init_columns(self):
        self.columns = [{
            "x": random.randint(0, self.sw),
            "y": random.uniform(-self.sh, 0),
            "h": random.randint(60, 200),
            "speed": random.uniform(1.5, 4),
            "bright": random.uniform(0.3, 1.0),
            "w": random.randint(1, 3),
        } for _ in range(8)]

    def _init_orbs(self):
        self.orbs = []
        for i in range(8):
            angle = math.pi * 2 * i / 8
            self.orbs.append({
                "angle": angle,
                "speed": random.uniform(0.003, 0.008) * random.choice([-1,1]),
                "dist":  random.randint(200, 320),
                "r":     random.uniform(4, 9),
                "phase": random.uniform(0, math.pi*2),
                "trail": []
            })

    def _init_scan_lines(self):
        self.scan_lines = [{
            "y":      random.randint(0, self.sh),
            "speed":  random.uniform(0.5, 2),
            "bright": random.uniform(0.05, 0.2)
        } for _ in range(6)]

    def _init_siri_blobs(self):
        # Organic color blobs that drift and morph — like Apple Siri
        hues = [0.53, 0.62, 0.72, 0.36, 0.45]  # cyan, blue, purple, green, teal
        self.siri_blobs = []
        for i in range(5):
            angle = math.pi * 2 * i / 5
            self.siri_blobs.append({
                "angle":  angle,
                "speed":  random.uniform(0.008, 0.02) * random.choice([-1,1]),
                "dist":   random.uniform(8, 22),
                "hue":    hues[i],
                "size":   random.uniform(18, 32),
                "phase":  random.uniform(0, math.pi*2),
                "morph":  random.uniform(0, math.pi*2),
            })

    # ── SPAWN HELPERS ─────────────────────────────────────────────
    def _spawn_particles(self, x, y, count=3):
        for _ in range(count):
            speed = random.uniform(0.3, 1.5)
            angle = random.uniform(0, math.pi*2)
            self.particles.append({
                "x": x, "y": y,
                "vx": math.cos(angle)*speed,
                "vy": math.sin(angle)*speed,
                "life": 1.0,
                "decay": random.uniform(0.015, 0.04),
                "r": random.uniform(1.5, 4),
                "trail": []
            })

    def _spawn_lightning(self, x1, y1, x2, y2, branches=3):
        segs = []
        def recurse(ax, ay, bx, by, depth):
            if depth == 0:
                segs.append((ax, ay, bx, by)); return
            mx = (ax+bx)/2 + random.uniform(-30, 30)
            my = (ay+by)/2 + random.uniform(-30, 30)
            recurse(ax, ay, mx, my, depth-1)
            recurse(mx, my, bx, by, depth-1)
            if random.random() < 0.4 and depth > 1:
                recurse(mx, my,
                        mx+random.uniform(-60,60),
                        my+random.uniform(-60,60), depth-2)
        recurse(x1, y1, x2, y2, branches)
        self.lightning.append({"segs": segs, "life": 1.0, "decay": 0.08})

    def _spawn_ring(self, x, y):
        self.rings.append({
            "x": x, "y": y, "r": 10,
            "max_r": random.randint(150, 280),
            "speed": random.uniform(3, 6),
            "life": 1.0, "decay": 0.012
        })

    def _spawn_siri_ripple(self):
        sz = 160
        self.siri_ripples.append({
            "r": 20, "max_r": sz//2 - 5,
            "life": 1.0, "decay": 0.025
        })

    # ── DRAW MINI — Siri-style organic circle ────────────────────
    def _draw_mini(self):
        c = self.canvas
        c.delete("all")
        sz  = 160
        cx  = sz // 2
        cy  = sz // 2
        R   = sz // 2 - 4   # main circle radius
        self.breath    += 0.04
        self.siri_phase += 0.03
        self.tick       += 1

        # Update blobs — state affects behavior
        active = self.state in ("listening", "speaking", "thinking")
        for blob in self.siri_blobs:
            spd = blob["speed"] * (2.5 if active else 1.0)
            blob["angle"] = (blob["angle"] + spd) % (math.pi*2)
            blob["morph"] += 0.03

        # Update siri wave
        if self.state in ("listening", "speaking"):
            self.siri_wave = [
                v*0.72 + random.uniform(-18, 18)*0.28
                for v in self.siri_wave]
        else:
            self.siri_wave = [v*0.88 for v in self.siri_wave]

        # ── 1. Clipping mask — dark circle bg
        # Draw multiple layered circles for depth
        for r in range(R, 0, -3):
            # radial gradient approximation
            t_ratio = r / R
            lum = 0.02 + (1-t_ratio) * 0.01
            fill = self._c(lum, 0.5)
            c.create_oval(cx-r, cy-r, cx+r, cy+r,
                          fill=fill, outline="")

        # ── 2. Organic color blobs (the Siri effect)
        for blob in self.siri_blobs:
            dist   = blob["dist"] * (1 + 0.4*math.sin(blob["morph"]))
            bx     = cx + dist * math.cos(blob["angle"])
            by     = cy + dist * math.sin(blob["angle"])
            size   = blob["size"] * (1 + 0.3*math.sin(blob["morph"]*1.3))
            # State modifies intensity
            intensity = 1.0 if active else 0.45
            hue = blob["hue"]
            # Multiple passes for soft glow
            for layer in range(6, 0, -1):
                lr   = size * (layer / 3.0)
                lum  = intensity * (0.08 + (6-layer)*0.06)
                lum  = min(0.7, lum)
                col  = self._c2(hue, lum, 1.0)
                c.create_oval(bx-lr, by-lr, bx+lr, by+lr,
                              fill=col, outline="")

        # ── 3. Waveform ring — organic breathing outline
        n   = len(self.siri_wave)
        pts = []
        for i in range(n):
            angle = math.radians(i * 360/n)
            # Wave amplitude varies by state
            amp   = 0.18 if active else 0.06
            wave_r = R * (0.82 + amp * math.sin(
                self.siri_wave[i]/18 + self.siri_phase + i*0.3))
            px = cx + wave_r * math.cos(angle)
            py = cy + wave_r * math.sin(angle)
            pts.extend([px, py])

        if len(pts) >= 4:
            # Glow outline
            c.create_polygon(pts, outline=self._c(0.3, 1.0),
                             fill="", width=4, smooth=True)
            c.create_polygon(pts, outline=self._c(0.6, 1.0),
                             fill="", width=2, smooth=True)
            c.create_polygon(pts, outline=self._c(0.9, 1.0),
                             fill="", width=1, smooth=True)

        # ── 4. Ripple rings
        if self.tick % 60 == 0 or (active and self.tick % 25 == 0):
            self._spawn_siri_ripple()
        dead = []
        for i, rip in enumerate(self.siri_ripples):
            rip["r"]    += 1.5
            rip["life"] -= rip["decay"]
            if rip["life"] <= 0 or rip["r"] > rip["max_r"]:
                dead.append(i); continue
            lum = rip["life"] * 0.4
            r2  = rip["r"]
            c.create_oval(cx-r2, cy-r2, cx+r2, cy+r2,
                          outline=self._c(lum, 1.0), width=1)
        for i in reversed(dead): self.siri_ripples.pop(i)

        # ── 5. Breathing center glow
        pulse = 1.0 + 0.15 * math.sin(self.breath * 2)
        core_intensity = 1.2 if active else 0.7
        for r2 in [22, 16, 10, 5, 2]:
            lum = core_intensity * (0.15 + (22-r2)*0.025)
            lum = min(0.85, lum) * pulse
            c.create_oval(cx-r2*pulse, cy-r2*pulse,
                          cx+r2*pulse, cy+r2*pulse,
                          fill=self._c(lum, 1.0), outline="")

        # ── 6. Sharp outer border ring
        c.create_oval(cx-R, cy-R, cx+R, cy+R,
                      outline=self._c(0.15, 1.0), width=2)
        c.create_oval(cx-R-2, cy-R-2, cx+R+2, cy+R+2,
                      outline=self._c(0.06, 1.0), width=3)

        # ── 7. Status text (minimal, elegant)
        smap = {
            "idle":      "",
            "listening": "◉",
            "thinking":  "⟳",
            "speaking":  "◆",
        }
        icon = smap.get(self.state, "")
        if icon:
            c.create_text(cx, cy + R + 12,
                          text=icon,
                          font=("Courier New", 10),
                          fill=self._c(0.5))

    # ── DRAW FULL ─────────────────────────────────────────────────
    def _draw_full(self):
        c  = self.canvas
        c.delete("all")
        sw, sh = self.sw, self.sh
        cx, cy = self.cx, self.cy
        col    = self._c(0.7)
        col_b  = self._c(0.9)
        col_d  = self._c(0.12)
        col_m  = self._c(0.4)
        self.breath += 0.03
        self.tick   += 1
        t = self.tick
        self.energy_pool = 0.7 + 0.3*math.sin(self.breath*1.5)
        ep = self.energy_pool

        # Scan lines
        for sl in self.scan_lines:
            sl["y"] = (sl["y"] + sl["speed"]) % sh
            for i in range(4, 0, -1):
                c.create_line(0, sl["y"]-i, sw, sl["y"]-i,
                              fill=self._c(sl["bright"]*(1-i/5)*ep, 0.8), width=1)
            c.create_line(0, sl["y"], sw, sl["y"],
                          fill=self._c(sl["bright"]*ep), width=1)

        # Light columns
        for col2 in self.columns:
            col2["y"] += col2["speed"]
            if col2["y"] > sh + 50:
                col2["y"]     = random.uniform(-200, -50)
                col2["x"]     = random.randint(0, sw)
                col2["bright"]= random.uniform(0.3, 1.0)
            x2 = col2["x"]; y2 = col2["y"]
            h2 = col2["h"]; br = col2["bright"] * ep
            for i in range(6, 0, -1):
                c.create_line(x2, y2-i*3, x2, y2,
                              fill=self._c(br*(1-i/7), 0.9),
                              width=col2["w"]+i)
            for i in range(h2):
                lum = br*(1-i/h2)*0.4
                if lum > 0.01:
                    c.create_line(x2, y2+i, x2, y2+i+1,
                                  fill=self._c(lum, 0.6), width=col2["w"])

        # Hex grid
        hex_r = 55
        for hx in range(-hex_r, sw+hex_r, int(hex_r*1.73)):
            for hy in range(-hex_r, sh+hex_r, hex_r*2):
                offset = hex_r if (hx//int(hex_r*1.73))%2==0 else 0
                self._hex(c, hx, hy+offset, hex_r-2, self._c(0.04, 0.5))

        # Shockwave rings
        if t % 90 == 0: self._spawn_ring(cx, cy)
        dead = []
        for i, ring in enumerate(self.rings):
            ring["r"]    += ring["speed"]
            ring["life"] -= ring["decay"]
            if ring["life"] <= 0 or ring["r"] > ring["max_r"]:
                dead.append(i); continue
            r2  = ring["r"]; lum = ring["life"] * 0.6
            for gw in [8, 5, 2]:
                c.create_oval(ring["x"]-r2, ring["y"]-r2,
                              ring["x"]+r2, ring["y"]+r2,
                              outline=self._c(lum*(gw/8), 1.0), width=gw)
        for i in reversed(dead): self.rings.pop(i)

        # Radar sweep
        self.radar_angle = (self.radar_angle + 1.8*ep) % 360
        self.radar_trail.append(self.radar_angle)
        if len(self.radar_trail) > 60: self.radar_trail.pop(0)
        radar_r = 260
        for i, ang in enumerate(self.radar_trail):
            fade = i/len(self.radar_trail); lum = fade*0.5*ep
            if lum < 0.01: continue
            rad = math.radians(ang)
            x2 = cx + radar_r*math.cos(rad)
            y2 = cy + radar_r*math.sin(rad)
            c.create_line(cx, cy, x2, y2,
                          fill=self._c(lum, 1.0), width=max(1, int(fade*4)))
        for gw in [6, 3, 1]:
            c.create_oval(cx-radar_r, cy-radar_r, cx+radar_r, cy+radar_r,
                          outline=self._c(0.08*gw/6), width=gw)
        rad   = math.radians(self.radar_angle)
        tip_x = cx + radar_r*math.cos(rad)
        tip_y = cy + radar_r*math.sin(rad)
        for gr in [12, 8, 4]:
            c.create_oval(tip_x-gr, tip_y-gr, tip_x+gr, tip_y+gr,
                          fill=self._c(0.5*(gr/12), 1.0), outline="")

        # Orbiting orbs
        for orb in self.orbs:
            orb["angle"] = (orb["angle"] + orb["speed"]*ep) % (math.pi*2)
            pulse = 1.0 + 0.3*math.sin(self.breath*2 + orb["phase"])
            ox = cx + orb["dist"]*math.cos(orb["angle"])
            oy = cy + orb["dist"]*math.sin(orb["angle"])
            orb["trail"].append((ox, oy))
            if len(orb["trail"]) > 20: orb["trail"].pop(0)
            for i in range(len(orb["trail"])-1):
                fade = i/len(orb["trail"])
                tx1,ty1 = orb["trail"][i]; tx2,ty2 = orb["trail"][i+1]
                c.create_line(tx1,ty1,tx2,ty2,
                              fill=self._c(fade*0.5, 1.0), width=1)
            r2 = orb["r"] * pulse
            for gr in [r2*3, r2*2, r2]:
                lum = 0.2 if gr==r2*3 else 0.4 if gr==r2*2 else 0.85
                c.create_oval(ox-gr,oy-gr,ox+gr,oy+gr,
                              fill=self._c(lum,1.0), outline="")
            c.create_line(cx,cy,ox,oy,fill=self._c(0.06),width=1,dash=(4,8))

        # Central core
        core_r = 40 + 8*math.sin(self.breath*2)*ep
        for i, r2 in enumerate([core_r*2.2, core_r*1.6, core_r*1.1, core_r]):
            lum = 0.15 + i*0.18; gw = 6-i
            c.create_oval(cx-r2-gw, cy-r2-gw, cx+r2+gw, cy+r2+gw,
                          outline=self._c(lum*0.4,1.0), width=gw*2)
            c.create_oval(cx-r2,cy-r2,cx+r2,cy+r2,
                          outline=self._c(lum,1.0), width=max(1,gw-1))
        burst = 15 + 5*math.sin(self.breath*3)*ep
        for i in range(12):
            ang = math.radians(i*30 + t*2)
            bx = cx + burst*math.cos(ang); by = cy + burst*math.sin(ang)
            lum = 0.5 + 0.4*math.sin(self.breath+i)
            c.create_line(cx,cy,bx,by,fill=self._c(lum,1.0),width=2)
        for r2 in [8,5,3,1]:
            c.create_oval(cx-r2,cy-r2,cx+r2,cy+r2,
                          fill=self._c(0.4+(8-r2)*0.07,1.0),outline="")
        c.create_oval(cx-1,cy-1,cx+1,cy+1,fill=WHITE,outline="")

        # Lightning
        self.lightning_timer += 1
        if self.lightning_timer > random.randint(25, 60):
            self.lightning_timer = 0
            if len(self.orbs) >= 2:
                a,b = random.sample(self.orbs, 2)
                ax=cx+a["dist"]*math.cos(a["angle"]); ay=cy+a["dist"]*math.sin(a["angle"])
                bx=cx+b["dist"]*math.cos(b["angle"]); by2=cy+b["dist"]*math.sin(b["angle"])
                self._spawn_lightning(ax,ay,bx,by2)
            if self.orbs:
                orb = random.choice(self.orbs)
                ox=cx+orb["dist"]*math.cos(orb["angle"])
                oy=cy+orb["dist"]*math.sin(orb["angle"])
                self._spawn_lightning(cx,cy,ox,oy,2)
            self._spawn_ring(cx,cy)
        dead_l = []
        for i, bolt in enumerate(self.lightning):
            bolt["life"] -= bolt["decay"]
            if bolt["life"] <= 0: dead_l.append(i); continue
            for x1,y1,x2,y2 in bolt["segs"]:
                lum = bolt["life"]*0.9
                c.create_line(x1,y1,x2,y2,fill=self._c(lum*0.4),width=4)
                c.create_line(x1,y1,x2,y2,fill=self._c(lum*0.7),width=2)
                c.create_line(x1,y1,x2,y2,
                              fill=WHITE if bolt["life"]>0.7 else self._c(lum),
                              width=1)
        for i in reversed(dead_l): self.lightning.pop(i)

        # Voice waveform
        if self.state in ("listening","speaking"):
            self.vwave=[v*0.72+random.uniform(-35,35)*0.28 for v in self.vwave]
            if t%8==0:
                n=len(self.vwave)
                peak_i=max(range(n),key=lambda i:abs(self.vwave[i]))
                px=cx-200+peak_i*(400/n); py=cy+self.vwave[peak_i]*0.5
                self._spawn_particles(px,py,count=3)
        else:
            self.vwave=[v*0.94 for v in self.vwave]
        n=len(self.vwave); total_w=sw*0.55; sx=cx-total_w/2; sp=total_w/n
        for i in range(n-1):
            x1=sx+i*sp; x2=sx+(i+1)*sp
            y1=cy+self.vwave[i]*0.45; y2=cy+self.vwave[i+1]*0.45
            dist=abs(i-n/2)/(n/2); lum=0.7-dist*0.4
            amp=abs(self.vwave[i])/35
            c.create_line(x1,y1,x2,y2,fill=self._c(0.2,1.0),width=4,smooth=True)
            c.create_line(x1,y1,x2,y2,fill=self._c(min(0.95,lum+amp*0.3),1.0),width=2,smooth=True)

        # Particles
        self._spawn_particles(cx,cy,count=1)
        dead_p=[]
        for i,p in enumerate(self.particles):
            p["trail"].append((p["x"],p["y"]))
            if len(p["trail"])>8: p["trail"].pop(0)
            p["x"]+=p["vx"]; p["y"]+=p["vy"]; p["vy"]+=0.05; p["life"]-=p["decay"]
            if p["life"]<=0: dead_p.append(i); continue
            for j in range(len(p["trail"])-1):
                fade=j/len(p["trail"])
                tx1,ty1=p["trail"][j]; tx2,ty2=p["trail"][j+1]
                c.create_line(tx1,ty1,tx2,ty2,fill=self._c(p["life"]*fade*0.6),width=1)
            r2=p["r"]*p["life"]
            c.create_oval(p["x"]-r2,p["y"]-r2,p["x"]+r2,p["y"]+r2,
                          fill=self._c(p["life"]*0.9,1.0),outline="")
        for i in reversed(dead_p): self.particles.pop(i)
        if len(self.particles)>200: self.particles=self.particles[-200:]

        # Glitch
        self.glitch_timer -= 1
        if self.glitch_timer <= 0:
            self.glitch_on=True; self.glitch_timer=random.randint(60,180)
        if self.glitch_on:
            for _ in range(random.randint(1,3)):
                gy=random.randint(0,sh); gh=random.randint(2,8); gx2=random.randint(-50,50)
                c.create_rectangle(gx2,gy,sw+gx2,gy+gh,fill=self._c(0.15,0.5),outline="")
            if random.random()<0.3: self.glitch_on=False

        # Corner brackets
        pad=30; s=45
        for bx,by,dx,dy in [(pad,pad,1,1),(sw-pad,pad,-1,1),
                              (pad,sh-pad,1,-1),(sw-pad,sh-pad,-1,-1)]:
            for gw in [4,2,1]:
                lum=0.2*(gw/4)+0.3
                c.create_line(bx,by,bx+dx*s,by,fill=self._c(lum),width=gw)
                c.create_line(bx,by,bx,by+dy*s,fill=self._c(lum),width=gw)
            c.create_oval(bx-3,by-3,bx+3,by+3,fill=col_b,outline="")

        # Panels
        self._panel_tl(c,col,col_m,col_d,col_b)
        self._panel_tr(c,col,col_m,col_d,col_b)
        self._panel_bl(c,col,col_m,col_d)
        self._panel_br(c,col,col_m,col_d,col_b)

        # Header
        gx2=random.randint(-2,2) if self.glitch_on else 0
        c.create_text(cx+gx2+2,28,text="N E X U S",font=("Courier New",26,"bold"),fill=self._c(0.25))
        c.create_text(cx+gx2,28,text="N E X U S",font=("Courier New",26,"bold"),fill=col_b)
        smap={"idle":"◈  STANDBY  ◈","listening":"◉  LISTENING  ◉",
              "thinking":"⟳  PROCESSING  ⟳","speaking":"◆  RESPONDING  ◆"}
        c.create_text(cx,60,text=smap.get(self.state,""),font=("Courier New",11),fill=col_m)
        c.create_line(cx-180,72,cx+180,72,fill=col_d,width=1)

        # Response text
        if self.shown_text:
            lines=self._wrap(self.shown_text,52)
            ty=cy+180
            for line in lines[-3:]:
                c.create_text(cx+1,ty+1,text=line,font=("Courier New",13),fill=self._c(0.2))
                c.create_text(cx,ty,text=line,font=("Courier New",13),fill=WHITE)
                ty+=24

        # Conversation
        y=sh-58
        c.create_line(cx-280,sh-72,cx+280,sh-72,fill=col_d,width=1)
        for role,text in reversed(self.conversation[-2:]):
            prefix="YOU  ›" if role=="user" else "NEXUS›"
            tc=WHITE if role=="user" else col_b
            short=text[:68]+"…" if len(text)>68 else text
            c.create_text(cx,y,text=f"{prefix}  {short}",font=("Courier New",11),fill=tc)
            y-=26
        c.create_text(cx,sh-12,text="CLICK FOR MINI  ·  ESC TO EXIT",font=("Courier New",8),fill=col_d)

    # ── HEX HELPER ────────────────────────────────────────────────
    def _hex(self, c, x, y, r, color):
        pts=[]
        for i in range(6):
            a=math.radians(60*i+30)
            pts.extend([x+r*math.cos(a),y+r*math.sin(a)])
        c.create_polygon(pts,outline=color,fill="",width=1)

    # ── PANELS ────────────────────────────────────────────────────
    def _panel_tl(self,c,col,col_m,col_d,col_b):
        x,y,w,h=25,90,255,200
        c.create_rectangle(x,y,x+w,y+h,fill=self._c(0.02),outline=col_d)
        for i in [1,2]:
            c.create_rectangle(x-i,y-i,x+w+i,y+h+i,fill="",outline=self._c(0.05+i*0.02))
        c.create_line(x,y,x+20,y,fill=col_b,width=2)
        c.create_line(x,y,x,y+20,fill=col_b,width=2)
        c.create_text(x+w//2,y+14,text="SYSTEM MATRIX",font=("Courier New",8,"bold"),fill=col_m)
        c.create_line(x+8,y+24,x+w-8,y+24,fill=col_d,width=1)
        for i,(lbl,val) in enumerate([
            ("PROC",psutil.cpu_percent()),
            ("MEMO",psutil.virtual_memory().percent),
            ("DISK",psutil.disk_usage('C:\\').percent)]):
            ty=y+36+i*52
            c.create_text(x+10,ty,text=lbl,font=("Courier New",8),fill=col_d,anchor="w")
            vc="#ff4466" if val>85 else col_b
            c.create_text(x+w-10,ty,text=f"{val:.0f}%",font=("Courier New",15,"bold"),fill=vc,anchor="e")
            bw=int((w-24)*val/100); bc="#ff4466" if val>85 else col
            c.create_rectangle(x+12,ty+14,x+w-12,ty+24,fill=self._c(0.04),outline=col_d)
            c.create_rectangle(x+12,ty+14,x+12+bw,ty+24,fill=self._c(0.15),outline="")
            c.create_rectangle(x+12,ty+16,x+12+bw,ty+22,fill=bc,outline="")
            if bw>4:
                for gi in range(4,0,-1):
                    c.create_line(x+12+bw,ty+14,x+12+bw,ty+24,fill=self._c(0.3*(gi/4)),width=gi*2)

    def _panel_tr(self,c,col,col_m,col_d,col_b):
        w2,h2=255,200; x=self.sw-w2-25; y=90
        c.create_rectangle(x,y,x+w2,y+h2,fill=self._c(0.02),outline=col_d)
        for i in [1,2]:
            c.create_rectangle(x-i,y-i,x+w2+i,y+h2+i,fill="",outline=self._c(0.05+i*0.02))
        c.create_line(x+w2,y,x+w2-20,y,fill=col_b,width=2)
        c.create_line(x+w2,y,x+w2,y+20,fill=col_b,width=2)
        c.create_text(x+w2//2,y+14,text="NETWORK I/O",font=("Courier New",8,"bold"),fill=col_m)
        c.create_line(x+8,y+24,x+w2-8,y+24,fill=col_d,width=1)
        try:
            net=psutil.net_io_counters()
            sent=net.bytes_sent/1024/1024; recv=net.bytes_recv/1024/1024
        except: sent=recv=0
        secs=int(time.time()-psutil.boot_time()); hh,rem=divmod(secs//60,60)
        now=datetime.now()
        for i,(lbl,val) in enumerate([("TX",f"{sent:.1f} MB"),("RX",f"{recv:.1f} MB"),("UP",f"{hh}h {rem}m")]):
            ty=y+36+i*45
            c.create_text(x+10,ty,text=lbl,font=("Courier New",8),fill=col_d,anchor="w")
            c.create_text(x+w2-10,ty,text=val,font=("Courier New",13,"bold"),fill=col_b,anchor="e")
            c.create_line(x+10,ty+18,x+w2-10,ty+18,fill=col_d,width=1,dash=(3,6))
        c.create_text(x+w2//2,y+h2-38,text=now.strftime("%I:%M:%S %p"),font=("Courier New",15,"bold"),fill=WHITE)
        c.create_text(x+w2//2,y+h2-16,text=now.strftime("%A  %d %B"),font=("Courier New",9),fill=col_m)

    def _panel_bl(self,c,col,col_m,col_d):
        x=25; y=self.sh-215; w2=255; h2=170
        c.create_rectangle(x,y,x+w2,y+h2,fill=self._c(0.02),outline=col_d)
        for i in [1,2]:
            c.create_rectangle(x-i,y-i,x+w2+i,y+h2+i,fill="",outline=self._c(0.04+i*0.02))
        c.create_line(x,y+h2,x+20,y+h2,fill=self._c(0.8),width=2)
        c.create_line(x,y+h2,x,y+h2-20,fill=self._c(0.8),width=2)
        c.create_text(x+w2//2,y+14,text="LAST COMMAND",font=("Courier New",8,"bold"),fill=col_m)
        c.create_line(x+8,y+24,x+w2-8,y+24,fill=col_d,width=1)
        if self.conversation:
            for i,(role,text) in enumerate(reversed(self.conversation[-3:])):
                ty=y+36+i*40; prefix="YOU" if role=="user" else "NXS"
                tc=WHITE if role=="user" else self._c(0.8)
                short=text[:24]+"…" if len(text)>24 else text
                c.create_text(x+10,ty,text=prefix,font=("Courier New",7,"bold"),fill=col_d,anchor="w")
                c.create_text(x+38,ty,text=short,font=("Courier New",9),fill=tc,anchor="w")

    def _panel_br(self,c,col,col_m,col_d,col_b):
        w2=255; h2=170; x=self.sw-w2-25; y=self.sh-215
        c.create_rectangle(x,y,x+w2,y+h2,fill=self._c(0.02),outline=col_d)
        for i in [1,2]:
            c.create_rectangle(x-i,y-i,x+w2+i,y+h2+i,fill="",outline=self._c(0.04+i*0.02))
        c.create_line(x+w2,y+h2,x+w2-20,y+h2,fill=col_b,width=2)
        c.create_line(x+w2,y+h2,x+w2,y+h2-20,fill=col_b,width=2)
        c.create_text(x+w2//2,y+14,text="POWER STATUS",font=("Courier New",8,"bold"),fill=col_m)
        c.create_line(x+8,y+24,x+w2-8,y+24,fill=col_d,width=1)
        bat=psutil.sensors_battery()
        if bat:
            pct=bat.percent; bc="#ff4466" if pct<20 else col
            for gx2 in [-1,0,1]:
                c.create_text(x+w2//2+gx2,y+65,text=f"{int(pct)}%",
                              font=("Courier New",30,"bold"),
                              fill=self._c(0.2) if gx2!=0 else bc)
            c.create_text(x+w2//2,y+98,
                          text="⚡ CHARGING" if bat.power_plugged else "● ON BATTERY",
                          font=("Courier New",9),fill=col_m)
            bw=int((w2-24)*pct/100)
            c.create_rectangle(x+12,y+112,x+w2-12,y+128,fill=self._c(0.04),outline=col_d)
            c.create_rectangle(x+12,y+112,x+12+bw,y+128,fill=self._c(0.15),outline="")
            c.create_rectangle(x+12,y+114,x+12+bw,y+126,fill=bc,outline="")
            if bw>4:
                for gi in range(4,0,-1):
                    c.create_line(x+12+bw,y+112,x+12+bw,y+128,fill=self._c(0.3*(gi/4)),width=gi*2)

    # ── UTILITIES ─────────────────────────────────────────────────
    def _wrap(self,text,width):
        words=text.split(); lines=[]; line=""
        for w in words:
            if len(line)+len(w)+1<=width:
                line+=("" if not line else " ")+w
            else:
                if line: lines.append(line)
                line=w
        if line: lines.append(line)
        return lines

    # ── MODE SWITCH ───────────────────────────────────────────────
    def _toggle_mode(self):
        if self.mode=="full": self._go_mini()
        else: self._go_full()

    def _go_mini(self):
        self.mode="mini"
        sz=160
        self.root.geometry(f"{sz}x{sz}+20+20")
        self.canvas.config(width=sz, height=sz)
        self.root.attributes('-alpha', 0.92)

    def _go_full(self):
        self.mode="full"
        self.root.geometry(f"{self.sw}x{self.sh}+0+0")
        self.canvas.config(width=self.sw, height=self.sh)
        self.root.attributes('-alpha', 0.97)

    # ── ANIMATE ───────────────────────────────────────────────────
    def _animate(self):
        if self.char_idx < len(self.full_text):
            self.char_idx = min(self.char_idx+3, len(self.full_text))
            self.shown_text = self.full_text[:self.char_idx]
        if self.visible:
            if self.mode=="full": self._draw_full()
            else: self._draw_mini()
        self.root.after(30, self._animate)

    # ── FADE ──────────────────────────────────────────────────────
    def _fade_in(self):
        if self.alpha < 0.97:
            self.alpha = min(0.97, self.alpha+0.08)
            self.root.attributes('-alpha', self.alpha)
            self.root.after(14, self._fade_in)

    def _fade_out(self):
        if self.alpha > 0.0:
            self.alpha = max(0.0, self.alpha-0.07)
            self.root.attributes('-alpha', self.alpha)
            self.root.after(14, self._fade_out)
        else: self.visible = False

    # ── PUBLIC API ────────────────────────────────────────────────
    def show(self):
        self.visible=True; self._fade_in()

    def set_state(self, state):
        self.state = state
        if not self.visible: self.show()

    def add_message(self, role, text):
        self.conversation.append((role, text))
        if len(self.conversation) > 12:
            self.conversation = self.conversation[-12:]
        if role == "nexus":
            self.full_text  = text
            self.char_idx   = 0
            self.shown_text = ""

    def _start_loops(self):
        self.root.after(0, self._animate)
        self.root.after(500, self.show)


# ── Global interface ──────────────────────────────────────────────
hud = None

def start_hud():
    global hud
    hud = NexusHUD()
    return hud

def set_state(state):
    if hud: hud.root.after(0, lambda: hud.set_state(state))

def add_message(role, text):
    if hud: hud.root.after(0, lambda: hud.add_message(role, text))