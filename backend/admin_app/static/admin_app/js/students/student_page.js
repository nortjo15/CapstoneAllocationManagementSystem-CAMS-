import { fetchStudents } from "./student_table.js";

// Load on page load
document.addEventListener("DOMContentLoaded", () => {
    fetchStudents();
})