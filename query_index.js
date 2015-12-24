LETTER_MASK = 0x1F;
FINAL_MASK = 1 << 5;
BFT_LAST_MASK = 1 << 6;

function TrieNode(trie, data) {
	this.edges = undefined;
	this.genitor = null;
	this.trie = trie;
	this.letter = String.fromCharCode((data & LETTER_MASK) + 'a'.charCodeAt(0));

	this.is_final = false;
	if (data & FINAL_MASK) {
		this.is_final = true;
	}

	this.bft_last = false;
	if (data & BFT_LAST_MASK) {
		this.bft_last = true;
	}

	this.first_child_id = data >> 7;
}

TrieNode.prototype.get_edges = function() {
	if (this.edges != undefined) {
		return this.edges;
	}

	this.edges = {}

	var next_id = this.first_child_id;

	while (next_id != 0) {
		var edge = this.trie.get_node_by_index(next_id);
		edge.genitor = this;
		if (edge.bft_last) {
			next_id = 0;
		} else {
			next_id += 1;
		}
		this.edges[edge.letter] = edge;
	}

	return this.edges;
};

TrieNode.prototype.get_word = function() {
	var ancestor = this.genitor;
	var word_array = [this.letter];

	while (ancestor != null) {
		if (ancestor.genitor != null) {
			word_array.push(ancestor.letter);
		}
		ancestor = ancestor.genitor;
	}

	return (word_array.reverse().join(''));
};

function bytes_to_uint32be(data, index) {
	var result = 0;
	var i = 0;

	while (i < 4) {
		result = result << 8;
		var val = (data[index * 4 + i].charCodeAt(0)) & 0xFF;
		result += val;
		i += 1;
	}

	return result;
}

function Trie(data) {
	this.data = data;
	this.root = this.get_node_by_index(0);
}

Trie.prototype.get_node_by_index = function(idx) {
	var uint32be = 	bytes_to_uint32be(this.data, idx);
	return new TrieNode(this, uint32be); 
};

Trie.prototype.lookup_node = function (word) {
	node = this.root;

	for (idx in word) {
		letter = word[idx];

		edges = node.get_edges();
		if (letter in edges) {
			node = edges[letter];
		} else {
			return null;
		}
	}

	return node;
}

Trie.prototype.exists = function (word) {
	var node = this.lookup_node(word);

	return (node != null && node.is_final);
};

Trie.prototype.lookup_completions = function (start_node, max_completions) {
	var completions = [];

	var queue = [[start_node]];
	var node = null;

	while (queue.length) {
		var path = queue.pop();
		var vertex = path[path.length - 1];
		var cnodes = vertex.get_edges();
		for (letter in cnodes) {
			node = cnodes[letter];

			if (node.is_final) {
				completions.push(node);
			}

			if (completions.length === max_completions) {
				console.log('found enough completions');
				queue = [];
				break;
			}

			var new_path = path.slice();
			new_path.push(node);
			queue.push(new_path);
		}
	}

	return completions;
}
