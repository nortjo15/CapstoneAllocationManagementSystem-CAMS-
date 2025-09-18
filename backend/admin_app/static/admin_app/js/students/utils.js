export function setButtonLoading(button, isLoading) 
{
  if (!button) return;
  if (isLoading) {
    button.classList.add("loading");
  } else {
    button.classList.remove("loading");
  }
}