/*
 * Developed by CQ Inversiones SAS. Copyright ©. 2019-2025. All rights reserved.
 * Desarrollado por CQ Inversiones SAS. Copyright ©. 2019-2025. Todos los derechos reservados.
 */

const ratings = document.querySelectorAll(".rating");
// Evento clic para cada estrella
ratings.forEach(function (rating) {
    const stars = rating.querySelectorAll(".star");
    stars.forEach(function (star, index) {
        star.addEventListener("click", function () {
            // Recorrer todas las estrellas y eliminar checked
            for (let i = 0; i < stars.length; i++) {
                stars[i].classList.remove("checked");
            }
            // Agregar checked a las estrellas
            for (let i = 0; i <= index; i++) {
                stars[i].classList.add("checked");
            }
            updateValueInputRating(rating, star.dataset.starvalue);
        });
    });
})

// Función para actualizar la interfaz de usuario
function updateValueInputRating(rating, val) {
    // Recorrer todas las estrellas y eliminar checked
    let inputRating = rating.getElementsByClassName("input-rating")[0];
    inputRating.value = val.toString();
}


// Obtener la calificación almacenada en local storage
//const storedRating = localStorage.getItem("rating");

// Si hay una calificación almacenada, actualizar la interfaz de usuario
//if (storedRating) {
//updateStarRating(storedRating);
//}
