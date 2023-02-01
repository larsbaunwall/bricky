export default async function (req, res) {
  const response = await fetch("http://api:8080/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question: req.body.question,
      history: req.body.history,
    }),
  });

  const data = await response.json();

  res.status(200).json({ result: data });
}
