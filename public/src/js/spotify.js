const variables = document.getElementById('variables')

const spotifyCards = document.querySelectorAll('.spotify-card')
const spotifyDropdown = document.querySelectorAll('.spotify-playlist-dropdown')
const returnButtons = document.querySelectorAll('.return-user-select')

const userSelect = document.getElementById('spotify-user-select')

const playlistUrlPrefix = "https://open.spotify.com/embed/playlist/"
const playlistUrlSuffix = "?utm_source=generator&theme=0"

const userPlaylistWrapper = {
  lenoxfro: document.getElementById('lenoxfro-playlist-wrapper'),
  dennis: document.getElementById('dennis-playlist-wrapper'),
  jens: document.getElementById('jens-playlist-wrapper')
}

returnButtons.forEach(button => {
  button.addEventListener('click', () => {
    toogleHide(userSelect)
    toogleHide(userPlaylistWrapper[variables.dataset.user])
  })
})

function toogleHide(element) {
  element.addEventListener('transitionend', () => { element.classList.remove('transition') })
  if (element.classList.contains('hidden')) {
    //show
    element.classList.add('transition')
    element.clientWidth
    element.classList.remove('hidden')
  } else {
    //hide
    element.classList.add('transition')
    element.classList.add('hidden')
  }
}

function insertAfter(newNode, existingNode) {
  existingNode.parentNode.insertBefore(newNode, existingNode.nextSibling)
}

function createNewPlayerRow(playlistId) {
  let tr = document.createElement('tr')
  let td = document.createElement('td')
  let iframe = createiFrame(playlistId)
  td.setAttribute('colspan', 4)

  td.appendChild(iframe)
  tr.appendChild(td)

  return tr
}

function createiFrame(playlistId, height = "80") {
  const playlistUrl = playlistUrlPrefix + playlistId + playlistUrlSuffix
  let iframe = document.createElement('iframe')

  iframe.src = playlistUrl
  iframe.width = "100%"
  iframe.height = height
  iframe.frameBorder = 0
  iframe.allowFullscreen = ""
  iframe.allow = "autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"

  return iframe
}

function createUUID() {
  var dt = new Date().getTime();
  var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    var r = (dt + Math.random() * 16) % 16 | 0;
    dt = Math.floor(dt / 16);
    return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
  });
  return uuid;
}

function addUserCard(user) {
  let div = document.createElement('div')
  let cardDiv = document.createElement('div')
  let img = document.createElement('img')
  let cardBody = document.createElement('div')
  let wrapper = document.createElement('div')
  let iframe = createiFrame(user.currentPlaylist.id, "280")

  div.classList.add('col-sm-6', 'col-lg-4')
  cardDiv.classList.add('card', 'text-white', 'spotify-card')
  cardDiv.dataset.user = user.name
  img.src = user.currentPlaylist.image
  img.alt = ""
  cardBody.classList.add('card-body', 'card-body', 'pb-0', 'd-flex', 'justify-content-between', 'align-items-start')
  wrapper.classList.add('c-chart-wrapper')

  wrapper.appendChild(iframe)
  cardDiv.appendChild(img)
  cardDiv.appendChild(cardBody)
  cardDiv.appendChild(wrapper)
  div.appendChild(cardDiv)

  userSelect.appendChild(div)

  div.addEventListener('click', (event) => {
    parentNode = event.target.closest('.spotify-card')
    toogleHide(userSelect)

    toogleHide(userPlaylistWrapper[parentNode.dataset.user])
    variables.dataset.user = parentNode.dataset.user
  })
}

function addPlaylistRow(user, playlist) {
  let tr = document.createElement('tr')
  let image = document.createElement('td')
  let name = document.createElement('td')
  let trackCount = document.createElement('td')

  tr.classList.add('spotify-playlist-dropdown')
  tr.dataset.playlist = playlist.id

  let imageDiv = document.createElement('div')
  let imageDivImg = document.createElement('img')
  let imageDivSpan = document.createElement('span')

  imageDiv.classList.add('c-avatar')
  imageDivImg.classList.add('c-avatar-img')
  imageDivImg.src = playlist.image
  imageDivSpan.classList.add('badge', 'badge-info')
  imageDivSpan.innerHTML = playlist.week

  imageDiv.appendChild(imageDivImg)
  imageDiv.appendChild(imageDivSpan)
  image.classList.add('text-center')
  image.appendChild(imageDiv)

  let nameDiv = document.createElement('div')
  let nameSub = document.createElement('div')
  let nameSubSpan = document.createElement('span')

  nameDiv.innerHTML = playlist.name
  nameSub.classList.add('small', 'text-muted')
  nameSubSpan.innerHTML = user.displayName

  nameSub.appendChild(nameSubSpan)
  name.appendChild(nameDiv)
  name.appendChild(nameSub)

  let trackCountDiv = document.createElement('div')
  let trackCountStrong = document.createElement('strong')

  trackCountDiv.classList.add('small', 'text-muted')
  trackCountDiv.innerHTML = "Track Count"
  trackCountStrong.innerHTML = playlist.trackCount
  trackCount.appendChild(trackCountDiv)
  trackCount.appendChild(trackCountStrong)

  tr.appendChild(image)
  tr.appendChild(name)
  tr.appendChild(trackCount)

  userPlaylistWrapper[user.name].querySelector('tbody').appendChild(tr)

  tr.addEventListener('click', (event) => {
    parentDropdownNode = event.target.closest('.spotify-playlist-dropdown')
    if (parentDropdownNode.dataset.listelement === undefined) {
      playerRow = createNewPlayerRow(parentDropdownNode.dataset.playlist)
      playerRow.id = createUUID()
      insertAfter(playerRow, parentDropdownNode)
      parentDropdownNode.dataset.listelement = playerRow.id
    } else {
      toogleHide(document.getElementById(parentDropdownNode.dataset.listelement))
    }
  })
}

window.onload = () => {
  //load playlist.json
  fetch('/assets/data/playlists.json')
    .then(response => response.json())
    .then(data => {
      data.users.forEach(user => {
        addUserCard(user)
        user.playlists.forEach(playlist => {
          addPlaylistRow(user, playlist)
        })
      })
    })
}