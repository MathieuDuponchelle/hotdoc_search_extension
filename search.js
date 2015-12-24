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

	var new_html = '<p>Results</p>';
	new_html += '<ul>';

	results = [];

	console.time('lookup');

	var node = trie.lookup_node (this.value);

	if (node != null && node.is_final) {
		results.push (this.value);
	} else if (node != null) {
		var completions = trie.lookup_completions(node, 5);
		for (idx in completions) {
			results.push(completions[idx].get_word());
		}
	}
	console.timeEnd('lookup');

	for (idx in results) {
		console.log(results[idx]);
		new_html += '<li>' + results[idx] + '</li>'
	}

	new_html += '</ul>';

	var result_area = document.getElementById('result_area');
	result_area.innerHTML = new_html;
};
