
const SENIOREASE_API=localStorage.getItem("seniorEaseApiUrl")||"http://127.0.0.1:8000";
let SENIOREASE_USER_ID=Number(localStorage.getItem("seniorEaseUserId")||0);
async function seApi(path,options={}){const res=await fetch(SENIOREASE_API+path,{...options,headers:{"Content-Type":"application/json",...(options.headers||{})}});const data=await res.json().catch(()=>({}));if(!res.ok)throw new Error(data.detail||"Backend request failed");return data}
async function seEnsureUser(){
  if(SENIOREASE_USER_ID)return SENIOREASE_USER_ID;
  let name=localStorage.getItem("seniorEaseUserName")||"Senior User";
  const phone=localStorage.getItem("seniorEaseUserPhone")||null;
  const language=localStorage.getItem("seniorEaseLanguage")||"en";
  const u=await seApi("/users",{method:"POST",body:JSON.stringify({name,phone,language})});
  SENIOREASE_USER_ID=u.user_id;localStorage.setItem("seniorEaseUserId",SENIOREASE_USER_ID);localStorage.setItem("seniorEaseUserName",name);return SENIOREASE_USER_ID;
}
async function refreshBackend(){
  const uid=await seEnsureUser();
  const [u,m,a,c,n]=await Promise.all([seApi("/users/"+uid),seApi("/medicines/"+uid),seApi("/appointments/"+uid),seApi("/emergency-contacts/"+uid),seApi("/notifications/"+uid)]);
  localStorage.setItem("seniorEaseBackendUser",JSON.stringify(u));localStorage.setItem("seniorEaseBackendMedicines",JSON.stringify(m.medicines));localStorage.setItem("seniorEaseBackendAppointments",JSON.stringify(a.appointments));localStorage.setItem("seniorEaseBackendContacts",JSON.stringify(c.contacts));localStorage.setItem("seniorEaseBackendNotifications",JSON.stringify(n.notifications));
  window.dispatchEvent(new CustomEvent("seniorEaseBackendUpdated",{detail:{user:u,medicines:m.medicines,appointments:a.appointments,contacts:c.contacts,notifications:n.notifications}}));
}
async function addAppointmentFromForm(){
  const uid=await seEnsureUser(), doctor=document.getElementById("bookDoctorSelect").value, date=document.getElementById("bookDate").value, slot=document.getElementById("bookSlot").value, notes=document.getElementById("bookNotes").value;
  await seApi("/appointments",{method:"POST",body:JSON.stringify({user_id:uid,doctor_name:doctor,hospital_name:"",treatment:notes,appointment_date:date,appointment_time:slot})});
  SeniorEaseApp.closeModal("modalBookAppt");SeniorEaseApp.showToast("Appointment saved.");await refreshBackend();
}
async function addContactFromForm(){
  const uid=await seEnsureUser(), raw=document.getElementById("contactNameInput").value, m=raw.match(/^(.+?)\s*\((.+)\)$/), name=m?m[1].trim():raw, relationship=m?m[2].trim():"";
  await seApi("/emergency-contacts",{method:"POST",body:JSON.stringify({user_id:uid,name,relationship,phone:document.getElementById("contactPhoneInput").value,priority:1})});
  SeniorEaseApp.closeModal("modalAddContact");SeniorEaseApp.showToast("Family contact saved.");await refreshBackend();
}
async function emergency(){
  const uid=await seEnsureUser();
  const send=async()=>{try{await seApi("/emergency/"+uid,{method:"POST"});SeniorEaseApp.showToast("Emergency alert sent.");}catch(e){alert(e.message)}};
  if(navigator.geolocation)navigator.geolocation.getCurrentPosition(async p=>{try{await seApi("/users/"+uid+"/location",{method:"PUT",body:JSON.stringify({latitude:p.coords.latitude,longitude:p.coords.longitude})})}finally{send()}},send);else send();
}
async function voice(text){try{const uid=await seEnsureUser();return await seApi("/assistant",{method:"POST",body:JSON.stringify({user_id:uid,command:text,language:window.SeniorEaseLanguage?.current||"en"})})}catch(e){console.warn(e)}}
window.SeniorEaseAPI={base:SENIOREASE_API,api:seApi,ensureUser:seEnsureUser,userId:()=>SENIOREASE_USER_ID};
window.SeniorEaseBackend={refresh:refreshBackend,addAppointmentFromForm,addContactFromForm,emergency,voice};
window.addEventListener("load",async()=>{try{await seEnsureUser();await refreshBackend()}catch(e){console.warn("Backend unavailable:",e.message)}});
