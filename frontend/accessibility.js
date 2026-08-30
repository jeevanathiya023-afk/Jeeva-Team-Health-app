
window.SeniorEaseA11y = {
  setFontScale(scale){
    document.documentElement.style.setProperty("--font-scale", scale);
    localStorage.setItem("seniorEaseFontScale", scale);
  },
  toggleTheme(){
    document.body.classList.toggle("high-contrast");
    localStorage.setItem("seniorEaseContrast", document.body.classList.contains("high-contrast")?"1":"0");
  },
  toggleVoiceGuide(){
    const on=localStorage.getItem("seniorEaseVoiceGuide")!=="0";
    localStorage.setItem("seniorEaseVoiceGuide",on?"0":"1");
    const label=document.getElementById("voiceGuideLabel");
    if(label) label.textContent=on?"Voice Guide: OFF":"Voice Guide: ON";
  },
  toggleLanguage(){ window.SeniorEaseLanguage?.toggle(); },
  init(){
    const s=parseFloat(localStorage.getItem("seniorEaseFontScale")||"1"); this.setFontScale(s);
    if(localStorage.getItem("seniorEaseContrast")==="1") document.body.classList.add("high-contrast");
  }
};
