
window.SeniorEaseReminders = {
  reminders:JSON.parse(localStorage.getItem("seniorEaseReminders")||"[]"),
  render(){const g=document.getElementById("remindersGrid");if(!g)return;g.innerHTML=this.reminders.length?this.reminders.map((r,i)=>`<article class="item-card"><h3>⏰ ${r.title}</h3><p>${r.type} · ${r.date} · ${r.time}</p><button class="btn-action-secondary" onclick="SeniorEaseReminders.remove(${i})">Done</button></article>`).join(""):"<article class='item-card'><h3>No reminders yet.</h3><p>Add a reminder for appointments, tests, family events or daily tasks.</p></article>"},
  addReminder(e){e.preventDefault();const title=document.getElementById("remindTitleInput")?.value||"", type=document.getElementById("remindTypeSelect")?.value||"general", date=document.getElementById("remindDateInput")?.value||"", time=document.getElementById("remindTimeInput")?.value||"";this.reminders.push({title,type,date,time});localStorage.setItem("seniorEaseReminders",JSON.stringify(this.reminders));SeniorEaseApp.closeModal("modalAddReminder");this.render();SeniorEaseApp.showToast("Reminder saved.");},
  remove(i){this.reminders.splice(i,1);localStorage.setItem("seniorEaseReminders",JSON.stringify(this.reminders));this.render();},
  playChime(){const C=new AudioContext(),o=C.createOscillator(),g=C.createGain();o.frequency.value=523;g.gain.value=.06;o.connect(g);g.connect(C.destination);o.start();setTimeout(()=>{o.frequency.value=659},180);setTimeout(()=>{o.stop();C.close()},360)},
  requestBrowserNotifications(){if("Notification" in window) Notification.requestPermission().then(x=>SeniorEaseApp.showToast("Notification permission: "+x))}
};
