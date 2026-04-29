async function addMatch() {
    const data = {
        team: document.getElementById('team').value,
        runs_scored: parseInt(document.getElementById('runs_scored').value),
        overs_faced: document.getElementById('overs_faced').value,
        runs_conceded: parseInt(document.getElementById('runs_conceded').value),
        overs_bowled: document.getElementById('overs_bowled').value
    };

    await fetch('http://127.0.0.1:5000/add_match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    alert("Match Added!");
}

async function getNRR() {
    const team = document.getElementById('team').value;

    const res = await fetch(`http://127.0.0.1:5000/nrr/${team}`);
    const data = await res.json();

    document.getElementById('result').innerText =
        `NRR: ${data.NRR}`;
}