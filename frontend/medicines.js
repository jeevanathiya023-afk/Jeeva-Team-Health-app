
window.SeniorEaseMedicines = {
  data:[],
  async load(){
    if(window.SeniorEaseBackend?.refresh) await SeniorEaseBackend.refresh();
    this.render(JSON.parse(localStorage.getItem("seniorEaseBackendMedicines")||"[]"));
  },
  render(rows){
    this.data=rows; const grid=document.getElementById("medicinesGrid"); if(!grid)return;
    grid.innerHTML=rows.length?rows.map(m=>`<article class="item-card"><h3>💊 ${m.name}</h3><p><b>Dosage:</b> ${m.dosage||"As prescribed"}</p><p><b>Time:</b> ${(m.schedule_times||[]).join(", ")||m.timing||"Not set"}</p><div class="item-actions"><button class="btn-action-primary" onclick="SeniorEaseMedicines.setStatus(${m.id},'taken')">✅ Mark Taken</button></div></article>`).join(""):"<article class='item-card'><h3>No medicines added yet.</h3><p>Tap Add New Medicine to add your prescription.</p></article>";
  },
  filter(){this.render(this.data)},
  async addMedicine(e){
    e.preventDefault();
    const uid=await SeniorEaseAPI.ensureUser(), slot=document.getElementById("medSlotSelect").value;
    const times={morning:"08:30",afternoon:"14:00",night:"20:30"};
    const name=document.getElementById("medNameInput")?.value||"", dosage=document.getElementById("medDosageInput")?.value||"";
    await SeniorEaseAPI.api("/medicines",{method:"POST",body:JSON.stringify({user_id:uid,name,dosage,timing:slot,schedule_times:[times[slot]]})});
    SeniorEaseApp.closeModal("modalAddMed"); SeniorEaseApp.showToast("Medicine saved."); await this.load();
  },
  setStatus(id,status){ SeniorEaseApp.showToast(status==="taken"?"Medicine marked as taken.":"Medicine status updated."); }
};
