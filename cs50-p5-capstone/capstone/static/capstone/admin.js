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

// IMAGES MANAGER
const PhotosUpload = {
    input: "",
    preview: document.querySelector('#photos-preview'),
    uploadLimit: 5,
    files: [],
    handleFileInput(event) {
        const { files: fileList } = event.target
        PhotosUpload.input = event.target

        if (PhotosUpload.hasLimit(event)) return

        // the use of 'Array.from()' is to transform the list received in 'fileList' into a 'Array' and can use the 'forEach' on it
        Array.from(fileList).forEach(file => {
            
            PhotosUpload.files.push(file)

            const reader = new FileReader()

            reader.onload = () => {
                const image = new Image()
                image.src = String(reader.result)

                const div = PhotosUpload.getContainer(image)
                if (PhotosUpload.preview)
                PhotosUpload.preview.appendChild(div)
            }

            reader.readAsDataURL(file)
        })

        PhotosUpload.input.files = PhotosUpload.getAllFiles()
    },
    hasLimit(event) {
        const { uploadLimit, input, preview } = PhotosUpload
        const { files: fileList } = input

        if (fileList.length > uploadLimit) {
            alert(`Envie no máximo ${uploadLimit} fotos`)
            event.preventDefault()
            return true
        }

        if (preview) {
            const photosDiv = []
            preview.childNodes.forEach(item => {
                if (item.classList && item.classList.value == "photo")
                    photosDiv.push(item)
            })

            const totalPhotos = fileList.length + photosDiv.length
            if (totalPhotos > uploadLimit) {
                alert(`Você atingiu o limite máximo de ${uploadLimit} fotos!`)
                event.preventDefault()
                return true
            }
        }

        return false
    },
    getAllFiles() {
        // ClipboardEvent is for Firefox, DataTransfer is for Chrome
        const dataTransfer = new ClipboardEvent("").clipboardData || new DataTransfer()

        PhotosUpload.files.forEach(file => dataTransfer.items.add(file))

        return dataTransfer.files
    },
    getContainer(image) {
        const div = document.createElement('div')
        div.classList.add('photo')

        div.onclick = PhotosUpload.removePhoto

        div.appendChild(image)

        div.appendChild(PhotosUpload.getRemoveButton())

        return div
    },
    getRemoveButton() {
        const button = document.createElement('i')
        button.classList.add('material-icons')
        button.innerHTML = "close"
        return button
    },
    removePhoto(event) {
        const photoDiv = event.target.parentNode // <div class="photo">
        const photosArray = Array.from(PhotosUpload.preview.children)
        const index = photosArray.indexOf(photoDiv)


        PhotosUpload.files.splice(index, 1)
        PhotosUpload.input.files = PhotosUpload.getAllFiles()

        photoDiv.remove()
    },
    removeOldPhoto(event) {
        const photoDiv = event.target.parentNode

        if (photoDiv.id) {
            const removedFiles = document.querySelector('input[name="removed_files"]')
            if (removedFiles) {
                removedFiles.value += `${photoDiv.id},`
            }
        }

        photoDiv.remove()
    }
}

// PUT to edit recipe
saveButton = document.querySelector('#form-update')
if (saveButton) {
    saveButton.onclick = () => { 
    
        // Save the updates into database
        fetch(`edit`, {
            method: 'PUT',
            body: JSON.stringify({
                title: document.querySelector('[name="title"]').value,
                chef: document.querySelector('[name="chef"]').value,
                ingredients: document.querySelector('[name="ingredients"]').value,
                preparation: document.querySelector('[name="preparation"]').value,
                information: document.querySelector('[name="information"]').value,
            })
        })
    }
}
