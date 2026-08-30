
window.SeniorEaseContacts = {
  data:[],
  async load(){await SeniorEaseBackend?.refresh?.();this.render(JSON.parse(localStorage.getItem("seniorEaseBackendContacts")||"[]"));},
  render(rows){this.data=rows;const g=document.getElementById("familyContactsGrid");if(!g)return;g.innerHTML=rows.length?rows.map(c=>`<article class="item-card"><h3>👤 ${c.name}</h3><p>${c.relationship||"Trusted contact"}</p><p>${c.phone}</p><div class="item-actions"><a class="btn-action-primary" href="tel:${c.phone}">📞 Call</a><a class="btn-action-secondary" href="sms:${c.phone}">💬 SMS</a></div></article>`).join(""):"<article class='item-card'><h3>No family contacts yet.</h3><p>Add a trusted family member or caregiver.</p></article>"},
  addContact(e){e.preventDefault();SeniorEaseBackend.addContactFromForm().catch(err=>alert(err.message));},
  simulateCall(phone,name){if(confirm("Call "+name+"?")) location.href="tel:"+phone;}
};
