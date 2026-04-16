document.addEventListener("DOMContentLoaded", function () {

    const applyBtn = document.getElementById("applyFilters");
    const clearBtn = document.getElementById("clearFilters");
    const closeBtn = document.getElementById("closeModal");
    const modal = document.getElementById("filterFamilyModal");
    const openBtn = document.getElementById("openFilter");

    const families = document.querySelectorAll(".pet-item");

    openBtn.addEventListener("click", function () {
        modal.classList.remove("hidden");
    });

    applyBtn.addEventListener("click", function () {
        const selected = getSelectedFilters();
        families.forEach(family => {
            let show = true;

            if (!matchesFilter(family.dataset.species.toLowerCase(), selected.species)) {
                show = false;
            }
            if (!matchesPets(family.dataset.pets, selected.pets)) {
                show = false;
            }
            if (!matchesOccupants(family.dataset.occupants, selected.occupants)) {
                show = false;
            }
            if (!matchesFilter(family.dataset.children.toLowerCase(), selected.children)) {
                show = false;
            }

            family.style.display = show ? "block" : "none";
        });

        modal.classList.add("hidden");
    });

    clearBtn.addEventListener("click", function () {
        document.querySelectorAll("input[type='checkbox']").forEach(cb => {
            cb.checked = false;
        });

        families.forEach(family => {
            family.style.display = "block";
        });
    });

    closeBtn.addEventListener("click", function () {
        modal.classList.add("hidden");
    });

    function getSelectedFilters() {
        return {
            species: getCheckedValues("species"),
            pets: getCheckedValues("pets"),
            occupants: getCheckedValues("occupants"),
            children: getCheckedValues("children"),
        };
    }

    function getCheckedValues(name) {
        return Array.from(
            document.querySelectorAll(`input[name='${name}']:checked`)
        ).map(cb => cb.value);
    }

    function matchesFilter(familiesValue, selectedArray) {
        if (selectedArray.length === 0) return true;
        return selectedArray.includes(familiesValue);
    }

    function matchesPets(familiesPets, selectedPets) {
        if (selectedPets.length === 0) return true;
        const pets = parseInt(familiesPets);

        return selectedPets.some(filter => {
            if (filter === "10over") return pets >= 10;
            return pets === parseInt(filter);
        });
    }

    function matchesOccupants(familiesOccupants, selectedOccupants) {
        if (selectedOccupants.length === 0) return true;
        const numOccupants = parseInt(familiesOccupants);

        return selectedOccupants.some(filter => {
            if (filter === "6over") return numOccupants >= 6;
            return numOccupants === parseInt(filter);
        });
    }

});