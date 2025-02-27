#include <fstream>
#include <iostream>
#include <optional>
#include <unordered_map>
#include <vector>
#define MIN_SUP 0.01
#define DATA_FILE "./Reviews Sample.txt"
#define DELIMITER ";"

using std::cout;
using std::endl;
using std::ifstream;
using std::ofstream;
using std::optional;
using std::string;
using std::unordered_map;
using std::vector;

struct WordRef {
    const char *start = nullptr;
    size_t length = 0;
    size_t tx_idx = 0;
};

struct Candidate {
    size_t count = 0;
    vector<WordRef> seq_db;
};

using Candidates = unordered_map<string, Candidate>;

optional<vector<string>> read_tx(const string &path)
{
    // open the file and ensure it is valid
    cout << "Attempting to read file: " << path << endl;
    ifstream input_file(path);
    if (!input_file) {
        cout << "Failed to open the file: " << path << endl;
        return std::nullopt;
    }
    cout << "File opened successfully." << endl;

    // read the file line by line and store the transactions
    string item;
    vector<string> transaction;
    while (getline(input_file, item)) {
        transaction.push_back(std::move(item));
    }

    // close the file and print the number of transactions read
    cout << "Read " << transaction.size() << " transactions." << endl;
    input_file.close();
    return transaction;
}

vector<WordRef> split(string &str, char delimiter, size_t tx_idx)
{
    vector<WordRef> result;
    size_t start = 0, end = 0;

    // capture all words, store their starting address, length, and transaction
    // index
    while ((end = str.find(delimiter, start)) != string::npos) {
        if (end > start) { // Avoid empty strings
            result.push_back({str.data() + start, end - start, tx_idx + 1});
        }
        start = end + 1;
    }

    // Capture last word
    if (start < str.length()) {
        result.push_back(
            {str.data() + start, str.length() - start, tx_idx + 1});
    }

    return result;
}

void init_candidates(Candidates &candidates, vector<string> &txs)
{
    // Initialize word-projected candidates from transactions
    // Each candidate is a word and its projected database
    cout << "Initializing candidates..." << endl;
    for (size_t i = 0; i < txs.size(); i++) {
        vector<WordRef> itemset = split(txs[i], ' ', i);

        // Avoid duplicate counting in the same transaction
        unordered_map<string, int> counted;
        for (size_t i = 0; i < itemset.size(); i++) {
            string key(itemset[i].start, itemset[i].length);
            if (i + 1 < itemset.size()) {
                candidates[key].seq_db.push_back(itemset[i + 1]);
            }

            // Ensure counting happens only once per word per transaction
            if (++counted[key] <= 1) {
                candidates[key].count++;
            }
        }
    }

    cout << "Initialized " << candidates.size() << " candidates." << endl;
}

void filter_candidates(Candidates &candidates, size_t tx_total)
{
    // Filter out candidates with support less than the minumum
    Candidates new_candidates;
    for (auto &[key, candidate] : candidates) {
        if ((double)candidate.count / (double)tx_total >= MIN_SUP) {
            new_candidates[key] = std::move(candidate);
        }
    }
    candidates = std::move(new_candidates);
}

void write_candidates(ofstream &output, const Candidates candidates)
{
    cout << "Writing candidates to file: " << endl;
    for (const auto &[key, candidate] : candidates) {
        output << candidate.count << ":" << key << endl;
    }
    cout << "Finished writing candidates to " << endl;
}

Candidates process_candidates(const Candidates &candidates, size_t tx_total)
{
    cout << "=== Processing Candidates (Total: " << candidates.size()
         << ") ===" << endl;

    Candidates new_candidates;
    size_t generated_count = 0;
    for (const auto &[key, candidate] : candidates) {
        cout << "Processing candidate: [" << key
             << "] (count: " << candidate.count << ")" << endl;

        unordered_map<string, size_t> counted;
        for (const auto &word_ref : candidate.seq_db) {
            // Skip invalid references
            if (!word_ref.start || word_ref.length == 0) {
                continue;
            }

            // Extract the next word
            string next_word(word_ref.start, word_ref.length);
            if (next_word.empty()) {
                continue; // Skip empty words
            }

            cout << "  Processing with next word: \"" << next_word << "\""
                 << endl;

            // Create the new sequence
            string new_seq = key + DELIMITER + next_word;

            // Ensure counting happens only once per transaction
            if (counted[new_seq] != word_ref.tx_idx) {
                new_candidates[new_seq].count++;
            }
            counted[new_seq] = word_ref.tx_idx;

            // Find the next word reference safely
            const char *next_start = word_ref.start + word_ref.length;

            // Move to the next word, skipping spaces
            while (*next_start == ' ') {
                next_start++;
            }

            // Prevent empty strings from being stored as candidates
            if (*next_start == '\0') {
                continue;
            }

            // Find the next word boundary
            const char *next_end = strchr(next_start, ' ');
            if (!next_end) {
                next_end = next_start + strlen(next_start);
            }

            // Prevent invalid pointer arithmetic
            if (next_end > next_start) {
                new_candidates[new_seq].seq_db.push_back(
                    {next_start, static_cast<size_t>(next_end - next_start),
                     word_ref.tx_idx});
                generated_count++;

                cout << "    Generated New Sequence: [" << new_seq
                     << "] (count: " << new_candidates[new_seq].count << ")"
                     << endl;
            }
        }
    }

    cout << "Generated " << generated_count
         << " new sequences before filtering." << endl;

    // filter out the candidates with support less than the minimum
    size_t before_filtering = new_candidates.size();
    filter_candidates(new_candidates, tx_total);
    size_t after_filtering = new_candidates.size();

    cout << "Filtering applied: " << before_filtering << " → "
         << after_filtering << " remaining." << endl;
    cout << "=== Finished Processing Candidates ===" << endl;

    return new_candidates;
}

int main()
{
    cout << "Program started." << endl;
    optional<vector<string>> tx_opt = read_tx(DATA_FILE);
    if (!tx_opt) {
        cout << "Error reading transactions. Exiting program." << endl;
        return -1;
    }

    vector<string> &txs = *tx_opt;
    Candidates candidates;
    ofstream answer("answer.txt");
    init_candidates(candidates, txs);
    filter_candidates(candidates, txs.size());
    write_candidates(answer, candidates);

    // Print candidates with the strings stored in the sequence database
    while (candidates.size() > 0) {
        candidates = process_candidates(candidates, txs.size());
        write_candidates(answer, candidates);
    }

    return 0;
}
