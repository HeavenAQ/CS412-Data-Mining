#include <fstream>
#include <iostream>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#define MIN_SUP 0.01
#define DATA_FILE "./categories.txt"

using Candidates = std::unordered_map<std::string, int>;
using std::cout;
using std::endl;
using std::getline;
using std::ifstream;
using std::ofstream;
using std::string;
using std::unordered_set;
using std::vector;

const string DELIMITER = ";";

unordered_set<string> split_to_set(string itemset)
{
    size_t pos = 0;
    auto parse_str = itemset;
    unordered_set<string> result;
    while ((pos = parse_str.find(DELIMITER)) != string::npos) {
        auto item = parse_str.substr(0, pos);
        result.insert(item);
        parse_str = parse_str.substr(pos + 1);
    }
    result.insert(parse_str);
    return result;
}

string set_to_string(unordered_set<string> set)
{
    string res = "";
    for (auto item : set) {
        res += item + DELIMITER;
    }
    res.pop_back();
    return res;
}

bool is_subset(unordered_set<string> set1, unordered_set<string> set2)
{
    for (const auto &item : set2) {
        if (set1.find(item) == set1.end())
            return false;
    }
    return true;
}

void freq1_sup_count(const string tx, Candidates &candidates)
{
    size_t pos = 0;
    string parse_str = tx;
    vector<string> result;
    while ((pos = parse_str.find(DELIMITER)) != string::npos) {
        auto item = parse_str.substr(0, pos);
        result.push_back(item);
        parse_str = parse_str.substr(pos + 1);
        candidates[item]++;
    }
    candidates[parse_str]++;
}

size_t gen_freq_1_candidates(string file_path, Candidates &candidates)
{
    cout << "Generating frequent 1-item candidates..." << endl;
    string tx;
    size_t n = 0;
    ifstream input_file(file_path);
    while (getline(input_file, tx)) {
        freq1_sup_count(tx, candidates);
        n++;
    }
    cout << "Total transactions processed: " << n << endl;
    return n;
}

Candidates trim_candidates(const Candidates candidates, size_t total_tx)
{
    cout << "Trimming candidates below minimum support..." << endl;
    Candidates new_candidates;
    for (auto itemset : candidates) {
        if ((double)itemset.second / (double)total_tx >= MIN_SUP) {
            new_candidates[itemset.first] = itemset.second;
        }
    }
    cout << "Remaining candidates: " << new_candidates.size() << endl;
    return new_candidates;
}

void write_candidates(string path, const Candidates candidates)
{
    cout << "Writing candidates to file: " << path << endl;
    ofstream output(path);
    for (auto itemset : candidates) {
        output << itemset.second << ":" << itemset.first << endl;
    }
}

void write_candidates(ofstream &output, const Candidates candidates)
{
    cout << "Writing candidates to file: " << endl;
    for (auto itemset : candidates) {
        output << itemset.second << ":" << itemset.first << endl;
    }
}

vector<string> candidate_keys(const Candidates candidates)
{
    vector<string> keys;
    keys.reserve(candidates.size());
    for (auto itemset : candidates)
        keys.push_back(itemset.first);
    return keys;
}

Candidates gen_candidates(const Candidates candidates)
{
    cout << "Generating new candidate itemsets..." << endl;
    auto keys = candidate_keys(candidates);
    Candidates new_candidates;
    for (size_t i = 0; i < keys.size(); i++) {
        auto itemset1 = split_to_set(keys[i]);
        for (size_t j = i + 1; j < keys.size(); j++) {
            auto itemset2 = split_to_set(keys[j]);
            // Find common elements
            unordered_set<string> common;
            for (const auto &item : itemset1)
                if (itemset2.find(item) != itemset2.end())
                    common.insert(item);

            // If they have exactly (n-1) common elements, merge them
            if (common.size() == itemset1.size() - 1) {
                unordered_set<string> merged = itemset1;
                for (const auto &item : itemset2)
                    merged.insert(item);

                auto set_str = set_to_string(merged);
                new_candidates[set_str] = 0;
            }
        }
    }
    cout << "Generated " << new_candidates.size() << " new candidates." << endl;
    return new_candidates;
}

void gen_freq_sets(Candidates &candidates)
{
    cout << "Calculating frequency of candidates..." << endl;
    ifstream input_file(DATA_FILE);
    string tx;
    while (getline(input_file, tx)) {
        auto tx_set = split_to_set(tx);
        for (auto &candidate : candidates) {
            auto itemset = split_to_set(candidate.first);
            if (is_subset(tx_set, itemset)) {
                std::cout << "Found subset: " << candidate.first << std::endl;
                candidate.second++;
            }
        }
    }
    cout << "Finish calculating frequency of candidates..." << endl;
}

int main(void)
{
    cout << "Starting Frequent Itemset Mining..." << endl;
    Candidates candidates;
    ofstream part2("part2.txt");

    auto total_tx = gen_freq_1_candidates(DATA_FILE, candidates);
    auto new_candidates = trim_candidates(candidates, total_tx);
    write_candidates("./part1.txt", new_candidates);
    write_candidates(part2, new_candidates);

    while (!new_candidates.empty()) {
        new_candidates = gen_candidates(new_candidates);
        if (new_candidates.empty()) {
            break;
        }
        gen_freq_sets(new_candidates);
        new_candidates = trim_candidates(new_candidates, total_tx);
        write_candidates(part2, new_candidates);
    }
    cout << "Frequent Itemset Mining Completed." << endl;
}
