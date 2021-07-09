// Listen 'click' event on a recipe and opens it
const recipes = document.querySelectorAll('.receita')

for (let recipe of recipes) {
    recipe.addEventListener('click', () => {
        window.location.href = `/recipes/${recipe.id}`
    })
}

// Hide and show recipe infos on preview
const hideShowButtons = document.querySelectorAll('.button')
const recipeInfos = document.querySelectorAll('.recipe-hide-show')

for (let i = 0; i < hideShowButtons.length; i++) {
    hideShowButtons[i].addEventListener('click', () => {
        if (recipeInfos[i].classList.contains('hidden')) {
            recipeInfos[i].classList.remove('hidden')
            hideShowButtons[i].textContent = "ESCONDER"
        } else {
            recipeInfos[i].classList.add('hidden')
            hideShowButtons[i].textContent = "MOSTRAR"
        }
    })
}

// Visually show the current page on navigation menu
const currentPage = location.pathname
const menuItems = document.querySelectorAll('nav a')

for (let item of menuItems) {
    if (currentPage.includes(item.getAttribute('href'))) {
        item.classList.add('active')
    }
}

// RECIPE GALLERY 
const ImageGallery = {
    highlight: document.querySelector('.gallery .highlight > img'),
    previews: document.querySelectorAll('.gallery-preview img'),
    setImage(e) {
        const { target } = e

        ImageGallery.previews.forEach(preview => preview.classList.remove('active'))
        target.classList.add('active')

        ImageGallery.highlight.src = target.src
    }
}
