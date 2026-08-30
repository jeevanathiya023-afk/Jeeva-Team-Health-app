
window.SeniorEaseVoice = {
  recognition:null,
  listening:false,
  speakText(text){
    if(!("speechSynthesis" in window)) return;
    speechSynthesis.cancel();
    const u=new SpeechSynthesisUtterance(text);
    u.lang=(window.SeniorEaseLanguage?.current==="ta")?"ta-IN":"en-IN";
    speechSynthesis.speak(u);
  },
  speakGreeting(){ this.speakText("Welcome to SeniorEase. You can open Doctors, Medicines, Reminders, Family Contacts, Settings, or Emergency Help."); },
  speakCurrentSection(){ const el=document.querySelector(".app-section.active"); this.speakText(el?.innerText?.slice(0,1200)||"SeniorEase"); },
  processVoiceCommand(command){
    const c=command.toLowerCase();
    if(c.includes("doctor")||c.includes("hospital")) SeniorEaseApp.navTo("health");
    else if(c.includes("medicine")) SeniorEaseApp.navTo("medicines");
    else if(c.includes("reminder")) SeniorEaseApp.navTo("reminders");
    else if(c.includes("family")||c.includes("call son")) SeniorEaseApp.navTo("family");
    else if(c.includes("setting")) SeniorEaseApp.navTo("settings");
    else if(c.includes("emergency")) SeniorEaseApp.navTo("emergency");
    else if(c.includes("tamil")) SeniorEaseA11y.toggleLanguage();
    else if(c.includes("large")) SeniorEaseA11y.setFontScale(1.4);
    if(window.SeniorEaseBackend?.voice) SeniorEaseBackend.voice(command,window.SeniorEaseLanguage?.current||"en");
  },
  toggleSpeechRecognition(){
    const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
    if(!SR){ document.getElementById("voiceStatusText").textContent="Voice recognition is not available in this browser."; return; }
    if(this.listening){this.recognition?.stop();return;}
    this.recognition=new SR(); this.recognition.lang=(window.SeniorEaseLanguage?.current==="ta")?"ta-IN":"en-IN";
    this.recognition.interimResults=false; this.listening=true;
    document.getElementById("voiceStatusText").textContent="Listening… please speak.";
    this.recognition.onresult=e=>{const text=e.results[0][0].transcript;document.getElementById("voiceStatusText").textContent="Heard: "+text;this.processVoiceCommand(text);};
    this.recognition.onerror=()=>{this.listening=false;document.getElementById("voiceStatusText").textContent="Could not hear clearly. Please try again.";};
    this.recognition.onend=()=>{this.listening=false;};
    this.recognition.start();
  }
};
