export function setButtonLoading(button, isLoading) 
{
  if (!button) return;
  if (isLoading) {
    button.classList.add("loading");
  } else {
    button.classList.remove("loading");
  }
}

export function showPageLoader() 
{
  const loader = document.getElementById("page-loader");
  if (loader) loader.classList.remove("d-none");
}

export function hidePageLoader() 
{
  const loader = document.getElementById("page-loader");
  if (loader) loader.classList.add("d-none");
}