function createIterator(array) {
    var nextIndex = 0;

    return {
       next: function() {
           return nextIndex < array.length ? array[nextIndex++] : false
       }
    };
}

audioList = Array.from(
  document.querySelector('div.audio_page__audio_rows_list._audio_page__audio_rows_list._audio_pl.audio_w_covers.audio_owner_list_canedit')
  .childNodes
)
.filter(el => ! Array.from(el.classList).includes("audio_claimed"));

window.__audioIterator = createIterator(audioList);
document.querySelector(".audio_page_player_btn.audio_page_player_repeat").click();

var nameList = [];

for (let audio of audioList) {
  let textArr = audio.innerText.split("\n").filter(Boolean);
  let name = textArr[0] + ' - ' + textArr[1]
  
  nameList.push(
    name
      .replace(/\//g, "")
      .replace(/\\/g, "")
      .replace(/\|/g, "")
      .replace(/\?/g, "")
      .replace(/\*/g, "")
      .replace(/:/g, "")
      .replace(/</g, "")
      .replace(/>/g, "")
      .replace(/"/g, "")
      .replace(/'/g, "")
      .replace(/\.$/, "")
      .replace(/ $/g, "")
     + ".mp3"
  );
}

return nameList;
