
window.SeniorEaseLanguage = {
  current: localStorage.getItem("seniorEaseLanguage") || "en",
  toggle(){
    this.current = this.current === "en" ? "ta" : "en";
    localStorage.setItem("seniorEaseLanguage", this.current);
    document.documentElement.lang = this.current === "ta" ? "ta" : "en";
    const label=document.getElementById("langLabel");
    if(label) label.textContent=this.current==="ta" ? "English" : "தமிழ் (Tamil)";
    if(window.SeniorEaseApp?.showToast) SeniorEaseApp.showToast(this.current==="ta"?"மொழி தமிழ் ஆக மாற்றப்பட்டது":"Language changed to English");
  }
};
