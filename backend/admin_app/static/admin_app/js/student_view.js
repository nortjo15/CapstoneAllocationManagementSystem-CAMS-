//Reset button 
document.getElementById('reset-btn').addEventListener('click', function() {
    window.location.href = this.dataset.url;
  });

//JS code for CWA Validation
/* Validation for the CWA inputs
- Enforce min < max
- Enforce max > min 
- Should be between 0 & 100 */
const cwaMinInput = document.getElementById('cwa_min');
const cwaMaxInput = document.getElementById('cwa_max');
let cwaErrorDivLocal = document.getElementById('cwa_error');
let formLocal = cwaMinInput.closest('form'); //find parent form
const submitButton = formLocal.querySelector('button[type="submit"]'); //find submit button

function validateCWA()
{
    let min = parseFloat(cwaMinInput.value);
    let max = parseFloat(cwaMaxInput.value);

    //Enforce min & max >= 0
    if (!isNaN(min) && min < 0)
    {
        min = 0;
        cwaMinInput.value = min;
    }
    if (!isNaN(max) && max < 0)
    {
        max = 0;
        cwaMaxInput.value = max;
    }

    //Enforce min & max <= 100
    if (!isNaN(max) && max > 100)
    {
        max = 100;
        cwaMaxInput.value = max;
    }
    if (!isNaN(min) && min > 100)
    {
        min = 100;
        cwaMinInput.value = min;
    }

    //Check min <= max
    if (!isNaN(min) && !isNaN(max) && min > max)
    {
        cwaErrorDivLocal.textContent = 'CWA Min cannot be greater than CWA Max.'; //display error
        cwaErrorDivLocal.style.display = 'block';
        submitButton.disabled = true; //disable submit button while invalid inputs 
    }
    else 
    {
        cwaErrorDivLocal.textContent = ''; //clear error
        cwaErrorDivLocal.style.display = 'none';
        submitButton.disabled = false;
    }
}
//Run validation on input changes
cwaMinInput.addEventListener('input', validateCWA);
cwaMaxInput.addEventListener('input', validateCWA);

//Validate when page loads
validateCWA()