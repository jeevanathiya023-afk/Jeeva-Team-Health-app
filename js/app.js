
window.SeniorEaseApp = {
  current:"home",
  navTo(page){
    this.current=page;
    document.querySelectorAll(".app-section").forEach(s=>s.classList.remove("active"));
    const sec=document.getElementById("sec"+page.charAt(0).toUpperCase()+page.slice(1));
    if(sec) sec.classList.add("active");
    const bc=document.getElementById("navBreadcrumb"); if(bc) bc.style.display=page==="home"?"none":"flex";
    const title=document.getElementById("currentPageTitle"); if(title) title.textContent=page.charAt(0).toUpperCase()+page.slice(1);
    if(page==="medicines") SeniorEaseMedicines.load();
    if(page==="family") SeniorEaseContacts.load();
    if(page==="reminders") SeniorEaseReminders.render();
    if(page==="health") this.renderHealth();
    window.scrollTo({top:0,behavior:"smooth"});
  },
  openModal(id){document.getElementById(id)?.classList.add("open");},
  closeModal(id){document.getElementById(id)?.classList.remove("open");},
  openBookModal(){this.openModal("modalBookAppt");},
  showToast(msg){const b=document.getElementById("toastBanner");if(!b)return;document.getElementById("toastMessage").textContent=msg;b.classList.add("show");clearTimeout(this._toast);this._toast=setTimeout(()=>b.classList.remove("show"),3000)},
  filterHealthcare(kind,btn){document.querySelectorAll(".tab-pills .tab-pill").forEach(x=>x.classList.remove("active"));btn?.classList.add("active");this.renderHealth(kind)},
  renderHealth(kind="all"){
    const g=document.getElementById("healthDirectoryGrid");if(!g)return;
    const docs=[
      ["Dr. K. Sundaram","General Physician","Apollo Clinic","general"],
      ["Dr. Radhika Krishnan","Heart Specialist","Fortis Hospital","heart"],
      ["Dr. R. Natarajan","Eye Specialist","Sankara Nethralaya","eye"],
      ["Dr. Meenakshi Sundaresan","Joint & Geriatric Specialist","Senior Care Clinic","general"]
    ];
    if(kind==="hospitals"){g.innerHTML=`<article class="item-card"><h3>🏥 Government Hospital</h3><p>24/7 emergency service · Nearby hospital search uses your current location.</p><a class="btn-action-primary" href="tel:108">📞 Call 108</a></article>`;return}
    const rows=kind==="all"?docs:docs.filter(d=>d[3]===kind);
    g.innerHTML=rows.map(d=>`<article class="item-card"><h3>👨‍⚕️ ${d[0]}</h3><p><b>${d[1]}</b></p><p>${d[2]}</p><button class="btn-action-primary" onclick="SeniorEaseApp.openBookModal()">📅 Book Appointment</button></article>`).join("");
  },
  saveAppointment(e){e.preventDefault();SeniorEaseBackend.addAppointmentFromForm().catch(err=>alert(err.message));},
  triggerEmergencyProtocol(){this.openModal("modalEmergency");let n=5,el=document.getElementById("sosCountdownNumber");el.textContent=n;clearInterval(this._sos);this._sos=setInterval(()=>{n--;el.textContent=n;if(n<=0){clearInterval(this._sos);this.confirmEmergencyImmediately()}},1000)},
  cancelEmergency(){clearInterval(this._sos);this.closeModal("modalEmergency");this.showToast("Emergency alert cancelled.");},
  confirmEmergencyImmediately(){clearInterval(this._sos);this.closeModal("modalEmergency");SeniorEaseBackend.emergency().catch(err=>alert(err.message));},
  filterHealthcare(){}
};
document.addEventListener("DOMContentLoaded",()=>{
  SeniorEaseA11y.init(); SeniorEaseReminders.render();
  SeniorEaseApp.renderHealth();
  const date=document.getElementById("bookDate"); if(date) date.min=new Date().toISOString().slice(0,10);
});
