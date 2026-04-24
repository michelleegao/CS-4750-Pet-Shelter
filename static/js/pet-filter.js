document.addEventListener("DOMContentLoaded", function () {

    const applyBtn = document.getElementById("applyFilters");
    const clearBtn = document.getElementById("clearFilters");
    const closeBtn = document.getElementById("closeModal");
    const modal = document.getElementById("filterPetModal");
    const openBtn = document.getElementById("openFilter");

    const pets = document.querySelectorAll(".pet-link");
    const toggle = document.getElementById("previousToggle");
    const curPets = document.getElementById("current-pet-grid");
    const prevPets = document.getElementById("previous-pet-grid");

    openBtn.addEventListener("click", function () {
        modal.classList.remove("hidden");
    });

    applyBtn.addEventListener("click", function () {
        const selected = getSelectedFilters();
        pets.forEach(pet => {
            let item = pet.querySelector(".pet-item");
            let show = true;

            if (!matchesFilter(item.dataset.species.toLowerCase(), selected.species)) {
                show = false;
            }
            if (!matchesAge(item.dataset.age, selected.age)) {
                show = false;
            }
            if (!matchesFilter(item.dataset.color.toLowerCase(), selected.color)) {
                show = false;
            }
            if (!matchesFilter(item.dataset.breed.toLowerCase(), selected.breed)) {
                show = false;
            }
            if (!matchesFilter(item.dataset.siblings.toLowerCase(), selected.siblings)) {
                show = false;
            }
            if (!matchesWeight(item.dataset.weight, selected.weight)) {
                show = false;
            }

            pet.classList.toggle("hidden", !show);
        });

        modal.classList.add("hidden");
    });

    clearBtn.addEventListener("click", function () {
        document.querySelectorAll("input[type='checkbox']").forEach(cb => {
            cb.checked = false;
        });

        pets.forEach(pet => {
            //pet.style.display = "block";
            pet.classList.remove("hidden");
        });
    });

    closeBtn.addEventListener("click", function () {
        modal.classList.add("hidden");
    });

    function getSelectedFilters() {
        return {
            species: getCheckedValues("species"),
            age: getCheckedValues("age"),
            color: getCheckedValues("color"),
            breed: getCheckedValues("breed"),
            siblings: getCheckedValues("siblings"),
            weight: getCheckedValues("weight")
        };
    }

    function getCheckedValues(name) {
        return Array.from(
            document.querySelectorAll(`input[name='${name}']:checked`)
        ).map(cb => cb.value);
    }

    function matchesFilter(petValue, selectedArray) {
        if (selectedArray.length === 0) return true;
        return selectedArray.includes(petValue);
    }

    function matchesAge(petAge, selectedAges) {
        if (selectedAges.length === 0) return true;
        const age = parseInt(petAge);

        return selectedAges.some(filter => {
            if (filter === "under1") return age <= 1;
            if (filter === "10over") return age >= 10;
            return age === parseInt(filter);
        });
    }

    function matchesWeight(petWeight, selectedWeight) {
        if (selectedWeight.length === 0) return true;
        const weight = parseInt(petWeight);

        return selectedWeight.some(filter => {
            if (filter === "under10") return weight < 10;
            if (filter === "10to20") return weight >= 10 && weight < 20;
            if (filter === "20to30") return weight >= 20 && weight < 30;
            if (filter === "30to40") return weight >= 30 && weight < 40;
            if (filter === "40to50") return weight >= 40 && weight < 50;
            if (filter === "over50") return weight >= 50;
        });
    }

    toggle.addEventListener("change", function(){
        if (this.checked){
            curPets.style.display = "none";
            prevPets.style.display = "grid";
        } else {
            curPets.style.display = "grid";
            prevPets.style.display = "none";
        }
    });

});

