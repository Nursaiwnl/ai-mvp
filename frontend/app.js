const btn = document.getElementById("btn");
const input = document.getElementById("input");
const out = document.getElementById("out");

btn.onclick = async () => {
  out.textContent = "Loading...";
  const res = await fetch("http://127.0.0.1:8000/api/process", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ data: input.value })
  });
  out.textContent = JSON.stringify(await res.json(), null, 2);
};
