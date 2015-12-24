var req = new XMLHttpRequest();
req.open("GET", "dumped.trie", true);
req.overrideMimeType('text\/plain; charset=x-user-defined');

var trie = undefined;

req.onload = function (event) {
	data = req.responseText;
	console.time('trie_creation');
	trie = new Trie(data);
	console.timeEnd('trie_creation');
};

req.send(null);

document.getElementById("lookup").onkeyup=function () {
	if (trie === undefined) {
		return;
	}

	console.time('lookup');
	console.log(this.value, trie.lookup(this.value));
	console.timeEnd('lookup');
};
