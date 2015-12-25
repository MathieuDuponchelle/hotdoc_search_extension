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
};

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
				queue = [];
				break;
			}

			var new_path = path.slice();
			new_path.push(node);
			queue.push(new_path);
		}
	}

	return completions;
};

function my_range (arg_one, arg_two) {
	var res = new Array();
	var start = 0;
	var end = arg_one;

	if (arg_two != undefined) {
		start = arg_one;
		end = arg_two;
	}

	var i = start;

	while (i < end) {
		res.push(i);
		i += 1;
	}

	return res;
}

Trie.prototype.search_recursive = function (node, letter, word, previous_row, results,
		max_cost) {
	var columns = word.length + 1;
	var current_row = [previous_row[0] + 1];

	var column = 1;
	while (column < columns) {
		var insert_cost = current_row[column - 1] + 1;
		var delete_cost = previous_row[column] + 1;

		var replace_cost;
		if (word[column - 1] != letter) {
			replace_cost = previous_row[column - 1] + 1;
		} else {
			replace_cost = previous_row[column - 1];
		}

		current_row.push(Math.min(insert_cost, delete_cost, replace_cost));

		column += 1;
	}

	if (current_row[current_row.length - 1] <= max_cost && node.is_final) {
		results[node.get_word()] = current_row[current_row.length - 1];
	}

	if (Math.min.apply(null, current_row) <= max_cost) {
		var edges = node.get_edges();
		for (var letter in edges) {
			this.search_recursive(edges[letter], letter, word, current_row,
					results, max_cost);
		}
	}
};

Trie.prototype.search = function (word, max_cost) {
	var corrections = {};
	var current_row = my_range(word.length + 1);
	var edges = this.root.get_edges();

	for (var letter in edges) {
		this.search_recursive(edges[letter], letter, word, current_row,
				corrections, max_cost);
	}

	return corrections;
};