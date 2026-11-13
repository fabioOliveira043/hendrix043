document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('input[type="number"]').forEach(input => {
    input.addEventListener("change", () => {
      const min = Number(input.min || 0), max = Number(input.max || 999);
      let value = Number(input.value || 0);
      input.value = Math.max(min, Math.min(max, value));
    });
  });
});
