from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import sqlite3, json, math

DB = "eldercare.db"
app = FastAPI(title="ElderCare Healthcare Assistant API", version="2.0.0")

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = db()
    c.executescript("""
    PRAGMA foreign_keys=ON;
    CREATE TABLE IF NOT EXISTS users(
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
      phone TEXT UNIQUE, language TEXT DEFAULT 'en',
      latitude REAL, longitude REAL, created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS emergency_contacts(
      id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
      name TEXT NOT NULL, phone TEXT NOT NULL, relationship TEXT,
      priority INTEGER DEFAULT 1,
      FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
    CREATE TABLE IF NOT EXISTS medicines(
      id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
      name TEXT NOT NULL, dosage TEXT, timing TEXT, food_instruction TEXT,
      doctor_name TEXT, start_date TEXT, end_date TEXT,
      active INTEGER DEFAULT 1, updated_at TEXT NOT NULL,
      FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
    CREATE TABLE IF NOT EXISTS medicine_schedules(
      id INTEGER PRIMARY KEY AUTOINCREMENT, medicine_id INTEGER NOT NULL,
      time TEXT NOT NULL,
      FOREIGN KEY(medicine_id) REFERENCES medicines(id) ON DELETE CASCADE);
    CREATE TABLE IF NOT EXISTS appointments(
      id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
      doctor_name TEXT, hospital_name TEXT, treatment TEXT,
      appointment_date TEXT NOT NULL, appointment_time TEXT NOT NULL,
      status TEXT DEFAULT 'scheduled', checked_in INTEGER DEFAULT 0,
      reminder_sent INTEGER DEFAULT 0, delay_notified INTEGER DEFAULT 0,
      FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
    CREATE TABLE IF NOT EXISTS notifications(
      id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
      title TEXT NOT NULL, message TEXT NOT NULL, type TEXT DEFAULT 'general',
      is_read INTEGER DEFAULT 0, created_at TEXT NOT NULL,
      FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
    CREATE TABLE IF NOT EXISTS emergency_events(
      id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
      latitude REAL, longitude REAL, status TEXT DEFAULT 'active',
      created_at TEXT NOT NULL, family_notified INTEGER DEFAULT 0,
      FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
    CREATE TABLE IF NOT EXISTS sync_events(
      id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
      entity TEXT NOT NULL, entity_id INTEGER, action TEXT NOT NULL,
      payload TEXT, created_at TEXT NOT NULL);
    """)
    c.commit(); c.close()

init_db()

def now(): return datetime.now().isoformat(timespec="seconds")
def exists(c, uid): return c.execute("SELECT 1 FROM users WHERE id=?", (uid,)).fetchone() is not None
def notify(c, uid, title, msg, typ):
    c.execute("INSERT INTO notifications(user_id,title,message,type,created_at) VALUES(?,?,?,?,?)",
              (uid,title,msg,typ,now()))

class UserCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    language: str = "en"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class Location(BaseModel):
    latitude: float
    longitude: float

class ContactCreate(BaseModel):
    user_id: int
    name: str
    phone: str
    relationship: Optional[str] = None
    priority: int = 1

class MedicineCreate(BaseModel):
    user_id: int
    name: str
    dosage: Optional[str] = None
    timing: Optional[str] = None
    food_instruction: Optional[str] = None
    doctor_name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    schedule_times: list[str] = []

class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    dosage: Optional[str] = None
    timing: Optional[str] = None
    food_instruction: Optional[str] = None
    doctor_name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    active: Optional[int] = None
    schedule_times: Optional[list[str]] = None

class AppointmentCreate(BaseModel):
    user_id: int
    doctor_name: Optional[str] = None
    hospital_name: Optional[str] = None
    treatment: Optional[str] = None
    appointment_date: str
    appointment_time: str

class VoiceCommand(BaseModel):
    user_id: int
    command: str
    language: str = "en"

class SyncItem(BaseModel):
    user_id: int
    entity: str
    entity_id: Optional[int] = None
    action: str
    payload: dict = {}

@app.get("/")
def root(): return {"application":"ElderCare Healthcare Assistant","status":"running"}

@app.get("/health")
def health(): return {"status":"healthy","database":"connected"}

@app.post("/users")
def create_user(x: UserCreate):
    c=db()
    if x.phone and c.execute("SELECT 1 FROM users WHERE phone=?", (x.phone,)).fetchone():
        c.close(); raise HTTPException(409,"Phone already registered")
    cur=c.execute("""INSERT INTO users(name,phone,language,latitude,longitude,created_at)
                     VALUES(?,?,?,?,?,?)""",
                  (x.name,x.phone,x.language,x.latitude,x.longitude,now()))
    uid=cur.lastrowid; c.commit(); c.close()
    return {"success":True,"user_id":uid}

@app.get("/users/{user_id}")
def get_user(user_id:int):
    c=db(); r=c.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone(); c.close()
    if not r: raise HTTPException(404,"User not found")
    return dict(r)

@app.put("/users/{user_id}/location")
def update_location(user_id:int, x:Location):
    c=db()
    if not exists(c,user_id): c.close(); raise HTTPException(404,"User not found")
    c.execute("UPDATE users SET latitude=?,longitude=? WHERE id=?",(x.latitude,x.longitude,user_id))
    c.commit(); c.close(); return {"success":True}

@app.put("/users/{user_id}/language/{language}")
def update_language(user_id:int, language:str):
    c=db()
    if not exists(c,user_id): c.close(); raise HTTPException(404,"User not found")
    c.execute("UPDATE users SET language=? WHERE id=?",(language,user_id))
    c.commit(); c.close(); return {"success":True,"language":language}

@app.post("/emergency-contacts")
def add_contact(x:ContactCreate):
    c=db()
    if not exists(c,x.user_id): c.close(); raise HTTPException(404,"User not found")
    cur=c.execute("""INSERT INTO emergency_contacts(user_id,name,phone,relationship,priority)
                     VALUES(?,?,?,?,?)""",(x.user_id,x.name,x.phone,x.relationship,x.priority))
    cid=cur.lastrowid; c.commit(); c.close(); return {"success":True,"contact_id":cid}

@app.get("/emergency-contacts/{user_id}")
def contacts(user_id:int):
    c=db(); rows=c.execute("SELECT * FROM emergency_contacts WHERE user_id=? ORDER BY priority,id",(user_id,)).fetchall()
    c.close(); return {"contacts":[dict(r) for r in rows]}

@app.delete("/emergency-contacts/{contact_id}")
def delete_contact(contact_id:int):
    c=db(); cur=c.execute("DELETE FROM emergency_contacts WHERE id=?",(contact_id,))
    c.commit(); c.close()
    if not cur.rowcount: raise HTTPException(404,"Contact not found")
    return {"success":True}

@app.post("/medicines")
def add_medicine(x:MedicineCreate):
    c=db()
    if not exists(c,x.user_id): c.close(); raise HTTPException(404,"User not found")
    cur=c.execute("""INSERT INTO medicines
      (user_id,name,dosage,timing,food_instruction,doctor_name,start_date,end_date,updated_at)
      VALUES(?,?,?,?,?,?,?,?,?)""",
      (x.user_id,x.name,x.dosage,x.timing,x.food_instruction,x.doctor_name,x.start_date,x.end_date,now()))
    mid=cur.lastrowid
    for t in x.schedule_times: c.execute("INSERT INTO medicine_schedules(medicine_id,time) VALUES(?,?)",(mid,t))
    notify(c,x.user_id,"Medicine Added",f"{x.name} was added to your medicine list.","medicine")
    c.commit(); c.close(); return {"success":True,"medicine_id":mid}

@app.get("/medicines/{user_id}")
def medicines(user_id:int):
    c=db(); rows=c.execute("SELECT * FROM medicines WHERE user_id=? AND active=1 ORDER BY id DESC",(user_id,)).fetchall()
    out=[]
    for r in rows:
        d=dict(r); ts=c.execute("SELECT time FROM medicine_schedules WHERE medicine_id=? ORDER BY time",(r["id"],)).fetchall()
        d["schedule_times"]=[t["time"] for t in ts]; out.append(d)
    c.close(); return {"medicines":out}

@app.get("/medicines/{user_id}/today")
def todays_medicines(user_id:int): return medicines(user_id)

@app.put("/medicines/{medicine_id}")
def update_medicine(medicine_id:int, x:MedicineUpdate):
    c=db(); old=c.execute("SELECT * FROM medicines WHERE id=?",(medicine_id,)).fetchone()
    if not old: c.close(); raise HTTPException(404,"Medicine not found")
    data=x.model_dump(exclude_unset=True); schedule=data.pop("schedule_times",None)
    fields=[]; vals=[]
    for k,v in data.items(): fields.append(f"{k}=?"); vals.append(v)
    if fields:
        fields.append("updated_at=?"); vals.append(now()); vals.append(medicine_id)
        c.execute(f"UPDATE medicines SET {','.join(fields)} WHERE id=?",vals)
    if schedule is not None:
        c.execute("DELETE FROM medicine_schedules WHERE medicine_id=?",(medicine_id,))
        for t in schedule: c.execute("INSERT INTO medicine_schedules(medicine_id,time) VALUES(?,?)",(medicine_id,t))
    notify(c,old["user_id"],"Prescription Updated","Your medicine prescription was updated.","prescription")
    c.commit(); c.close(); return {"success":True}

@app.delete("/medicines/{medicine_id}")
def remove_medicine(medicine_id:int):
    c=db(); old=c.execute("SELECT * FROM medicines WHERE id=?",(medicine_id,)).fetchone()
    if not old: c.close(); raise HTTPException(404,"Medicine not found")
    c.execute("UPDATE medicines SET active=0,updated_at=? WHERE id=?",(now(),medicine_id))
    c.commit(); c.close(); return {"success":True}

@app.post("/appointments")
def add_appointment(x:AppointmentCreate):
    c=db()
    if not exists(c,x.user_id): c.close(); raise HTTPException(404,"User not found")
    cur=c.execute("""INSERT INTO appointments
      (user_id,doctor_name,hospital_name,treatment,appointment_date,appointment_time)
      VALUES(?,?,?,?,?,?)""",
      (x.user_id,x.doctor_name,x.hospital_name,x.treatment,x.appointment_date,x.appointment_time))
    aid=cur.lastrowid
    notify(c,x.user_id,"Medical Appointment",f"Appointment on {x.appointment_date} at {x.appointment_time}.","appointment")
    c.commit(); c.close(); return {"success":True,"appointment_id":aid}

@app.get("/appointments/{user_id}")
def appointments(user_id:int):
    c=db(); rows=c.execute("""SELECT * FROM appointments WHERE user_id=?
                              ORDER BY appointment_date,appointment_time""",(user_id,)).fetchall()
    c.close(); return {"appointments":[dict(r) for r in rows]}

@app.post("/appointments/{appointment_id}/check-in")
def check_in(appointment_id:int):
    c=db(); a=c.execute("SELECT * FROM appointments WHERE id=?",(appointment_id,)).fetchone()
    if not a: c.close(); raise HTTPException(404,"Appointment not found")
    c.execute("UPDATE appointments SET checked_in=1,status='attended' WHERE id=?",(appointment_id,))
    c.commit(); c.close(); return {"success":True}

@app.post("/appointments/{appointment_id}/delay-check")
def delay_check(appointment_id:int):
    c=db(); a=c.execute("SELECT * FROM appointments WHERE id=?",(appointment_id,)).fetchone()
    if not a: c.close(); raise HTTPException(404,"Appointment not found")
    if a["checked_in"]: c.close(); return {"delayed":False}
    c.execute("UPDATE appointments SET delay_notified=1 WHERE id=?",(appointment_id,))
    notify(c,a["user_id"],"Appointment Delay","You may be late for your medical appointment.","appointment_delay")
    c.commit(); c.close()
    return {"delayed":True,"family_notification_required":True}

@app.get("/notifications/{user_id}")
def notifications(user_id:int, unread_only:bool=False):
    c=db()
    q="SELECT * FROM notifications WHERE user_id=?"
    if unread_only: q+=" AND is_read=0"
    q+=" ORDER BY created_at DESC"
    rows=c.execute(q,(user_id,)).fetchall(); c.close()
    return {"notifications":[dict(r) for r in rows]}

@app.post("/notifications/{notification_id}/read")
def read_notification(notification_id:int):
    c=db(); cur=c.execute("UPDATE notifications SET is_read=1 WHERE id=?",(notification_id,))
    c.commit(); c.close()
    if not cur.rowcount: raise HTTPException(404,"Notification not found")
    return {"success":True}

@app.post("/emergency/{user_id}")
def emergency(user_id:int):
    c=db(); u=c.execute("SELECT * FROM users WHERE id=?",(user_id,)).fetchone()
    if not u: c.close(); raise HTTPException(404,"User not found")
    cur=c.execute("""INSERT INTO emergency_events
      (user_id,latitude,longitude,status,created_at,family_notified)
      VALUES(?,?,?,?,?,1)""",
      (user_id,u["latitude"],u["longitude"],"active",now()))
    eid=cur.lastrowid
    contacts=c.execute("SELECT * FROM emergency_contacts WHERE user_id=? ORDER BY priority,id",(user_id,)).fetchall()
    notify(c,user_id,"EMERGENCY","Emergency mode activated. Please stay calm.","emergency")
    c.commit(); c.close()
    return {"success":True,"emergency_id":eid,"status":"active",
            "location":{"latitude":u["latitude"],"longitude":u["longitude"]},
            "family_contacts":[dict(x) for x in contacts],
            "mobile_action":"Mobile app should request permission and initiate the appropriate emergency call/alert."}

@app.post("/emergency/{event_id}/cancel")
def cancel_emergency(event_id:int):
    c=db(); cur=c.execute("UPDATE emergency_events SET status='cancelled' WHERE id=?",(event_id,))
    c.commit(); c.close()
    if not cur.rowcount: raise HTTPException(404,"Emergency event not found")
    return {"success":True}

def dist(a,b,c,d):
    r=6371; p1=math.radians(a); p2=math.radians(c)
    dp=math.radians(c-a); dl=math.radians(d-b)
    z=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(math.sqrt(z))

@app.get("/hospitals/nearby")
def nearby_hospitals(latitude:float,longitude:float):
    hospitals=[
      {"name":"Government Hospital","latitude":13.0827,"longitude":80.2707,"open":True,"emergency_available":True,"phone":"0000000000"},
      {"name":"City General Hospital","latitude":13.0674,"longitude":80.2376,"open":True,"emergency_available":True,"phone":"0000000000"},
      {"name":"Emergency Care Hospital","latitude":13.0475,"longitude":80.2090,"open":True,"emergency_available":True,"phone":"0000000000"}]
    for h in hospitals: h["distance_km"]=round(dist(latitude,longitude,h["latitude"],h["longitude"]),2)
    hospitals.sort(key=lambda x:x["distance_km"])
    return {"source":"demo","hospitals":hospitals}

LANGUAGES={"en":"English","ta":"Tamil","hi":"Hindi","te":"Telugu","ml":"Malayalam","kn":"Kannada"}

@app.get("/languages")
def languages(): return LANGUAGES

def intent(text):
    t=text.lower()
    if any(w in t for w in ["emergency","help me","save me","danger","ambulance","அவசரம்","உதவி"]): return "EMERGENCY"
    if any(w in t for w in ["medicine","medicines","tablet","pill","medication","மருந்து","மாத்திரை"]): return "MEDICINE"
    if any(w in t for w in ["appointment","doctor","மருத்துவர்","அப்பாயின்ட்மெண்ட்"]): return "APPOINTMENT"
    if any(w in t for w in ["hospital","nearby hospital","nearest hospital","மருத்துவமனை"]): return "HOSPITAL"
    return "UNKNOWN"

RESP={
 "en":{"EMERGENCY":"Emergency mode is activated. Please stay calm.","MEDICINE":"I will check your medicines.","APPOINTMENT":"I will check your appointments.","HOSPITAL":"I will help you find a nearby hospital.","UNKNOWN":"Sorry, I did not understand. Please speak again."},
 "ta":{"EMERGENCY":"அவசரநிலை தொடங்கப்பட்டது. தயவுசெய்து அமைதியாக இருங்கள்.","MEDICINE":"உங்களுடைய மருந்துகளை சரிபார்க்கிறேன்.","APPOINTMENT":"உங்களுடைய மருத்துவ சந்திப்புகளை சரிபார்க்கிறேன்.","HOSPITAL":"அருகிலுள்ள மருத்துவமனையை கண்டுபிடிக்க உதவுகிறேன்.","UNKNOWN":"மன்னிக்கவும். புரியவில்லை. மீண்டும் பேசுங்கள்."},
 "hi":{"EMERGENCY":"आपातकाल सक्रिय है। कृपया शांत रहें।","MEDICINE":"मैं आपकी दवाइयों की जानकारी देखता हूँ।","APPOINTMENT":"मैं आपकी डॉक्टर की अपॉइंटमेंट देखता हूँ।","HOSPITAL":"मैं पास का अस्पताल खोजने में मदद करूंगा।","UNKNOWN":"माफ कीजिए, मैं समझ नहीं पाया। फिर से बोलिए।"}
}

@app.post("/voice/command")
def voice_command(x:VoiceCommand):
    i=intent(x.command); lang=x.language if x.language in RESP else "en"
    return {"user_id":x.user_id,"language":lang,"intent":i,"response_text":RESP[lang][i],"tts_required":True}

@app.post("/assistant")
def assistant(x:VoiceCommand):
    i=intent(x.command); c=db()
    if i=="MEDICINE":
        rows=c.execute("SELECT name FROM medicines WHERE user_id=? AND active=1",(x.user_id,)).fetchall()
        c.close(); return {"intent":i,"response":("Your medicines are: "+", ".join(r["name"] for r in rows)+".") if rows else "You have no active medicines.","speak_response":True}
    if i=="APPOINTMENT":
        a=c.execute("""SELECT * FROM appointments WHERE user_id=? AND status='scheduled'
                      ORDER BY appointment_date,appointment_time LIMIT 1""",(x.user_id,)).fetchone()
        c.close()
        text=f"Your next appointment is with {a['doctor_name'] or 'your doctor'} on {a['appointment_date']} at {a['appointment_time']}." if a else "You do not have any upcoming appointments."
        return {"intent":i,"response":text,"speak_response":True}
    if i=="EMERGENCY":
        c.close(); return {"intent":i,"response":"Emergency mode activated. Please stay calm.","action":"Call emergency contact","speak_response":True}
    if i=="HOSPITAL":
        u=c.execute("SELECT latitude,longitude FROM users WHERE id=?",(x.user_id,)).fetchone(); c.close()
        if not u: raise HTTPException(404,"User not found")
        return {"intent":i,"response":"I will help you find the nearest hospital.","latitude":u["latitude"],"longitude":u["longitude"]}
    c.close(); return {"intent":"UNKNOWN","response":"Sorry, I did not understand. Please speak again.","speak_response":True}

@app.post("/sync/push")
def sync_push(x:SyncItem):
    c=db(); cur=c.execute("""INSERT INTO sync_events
      (user_id,entity,entity_id,action,payload,created_at) VALUES(?,?,?,?,?,?)""",
      (x.user_id,x.entity,x.entity_id,x.action,json.dumps(x.payload),now()))
    sid=cur.lastrowid; c.commit(); c.close(); return {"success":True,"sync_id":sid}

@app.get("/sync/pull/{user_id}")
def sync_pull(user_id:int):
    c=db(); rows=c.execute("SELECT * FROM sync_events WHERE user_id=? ORDER BY id",(user_id,)).fetchall(); c.close()
    return {"events":[{"id":r["id"],"entity":r["entity"],"entity_id":r["entity_id"],"action":r["action"],"payload":json.loads(r["payload"] or "{}"),"created_at":r["created_at"]} for r in rows]}

@app.get("/dashboard/{user_id}")
def dashboard(user_id:int):
    c=db()
    if not exists(c,user_id): c.close(); raise HTTPException(404,"User not found")
    m=c.execute("SELECT COUNT(*) n FROM medicines WHERE user_id=? AND active=1",(user_id,)).fetchone()["n"]
    a=c.execute("SELECT COUNT(*) n FROM appointments WHERE user_id=? AND status='scheduled'",(user_id,)).fetchone()["n"]
    n=c.execute("SELECT COUNT(*) n FROM notifications WHERE user_id=? AND is_read=0",(user_id,)).fetchone()["n"]
    e=c.execute("SELECT COUNT(*) n FROM emergency_contacts WHERE user_id=?",(user_id,)).fetchone()["n"]
    c.close(); return {"user_id":user_id,"active_medicines":m,"upcoming_appointments":a,"unread_notifications":n,"emergency_contacts":e}
