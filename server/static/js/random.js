var facts = ["I will add more facts later", 'Heaven']
var randomFact = randomlist(facts);

function generateFacts() {
  document.getElementById('here').innerHTML = randomFact;
}

function randomlist(list) {
  var x = Math.floor(Math.random() * list.length);
  return list[x];
}