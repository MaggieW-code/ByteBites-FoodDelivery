const container = document.querySelector(".container");

if (!container) {
    throw new Error(
        "Root container was not found"
    );
}