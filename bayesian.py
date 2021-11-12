class Node(object):
    def __init__(self, name):
        self.name = name
        self.fathers = []
        self.CPT = {}

    def add_father(self, father):
        self.fathers.append(father)

    def multi_parent(self, node_tuple):
        _ , value = Node.search(node_tuple, self.name)
        if not len(self.fathers):
            return self.CPT[tuple([(self.name, value)])]

        temp = [(self.name, value)]
        for father in self.fathers:
            temp.append(Node.search(node_tuple, father))
        return self.CPT[tuple(temp)]

    def search(node_tuple, name):
        for (node, val) in node_tuple:
            if node == name:
                return (node, val)

class BayesianNetwork(object):
    def __init__(self, file):
        with open(file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()]
            data = [line for line in lines if line != '']

        self.total_node = int(lines[0])
        self.nodes = [Node(name) for name in data[1].split()]

        row = 2
        for i in range(self.total_node):
            for j, value in enumerate(data[row].split()):
                if value == '1':
                    self.nodes[j].add_father(self.nodes[i].name)
            row += 1

        for node in self.nodes:
            line = pow(2, len(node.fathers))
            
            for i in range(line):
                str_binary = bin(i).replace('0b','')
                bin_list = list(str_binary)
                while len(bin_list) < len(node.fathers):
                    bin_list.insert(0, '0')
                    
                str_binary = ''.join(bin_list)
                temp = []
                for j, father in enumerate(node.fathers):
                    temp.append((father, 'true' if str_binary[j] == '1' else 'false'))
                        
                temp2 = temp.copy()
                temp.insert(0, (node.name, 'true'))
                temp2.insert(0, (node.name, 'false'))
                
                node.CPT[tuple(temp)] = float(data[row + i].split()[0])
                node.CPT[tuple(temp2)] = float(data[row + i].split()[1])
            row += line

    def _parse_query(self, file):
        with open(file, 'r') as f:
            lines = f.readlines()
            
        query = []
        for line in lines:
            line = line.replace('P(', '').replace(')', '').replace('|', '').replace(',', ' ')
            line = line.strip().split()
            if not len(line):
                continue
            q1, q2 = [], []
            q1.append((line[0],'false'))
            q2.append((line[0],'true'))
            
            for i in range(1, len(line)):
                tmp = line[i].split('=')
                q1.append(tmp)
                q2.append((tmp[0],tmp[1]))
                
            query.append(tuple(q1))
            query.append(tuple(q2))
        return query

    def compute_query(self, file):
        for query in self._parse_query(file):
            result = str("{:.8f}".format(self.compute(query)))
            print(f'P{query[0]} | {query[1:]}\t=\t{result}')

    def compute(self, query):
        if len(query) == 1:
            return self.compute_lacks(list(query))
        return self.compute_lacks(list(query)) / self.compute_lacks(list(query)[1:])

    def compute_lacks(self, node_tuple):
        lack_nodes = [node.name for node in self.nodes if (node.name, 'true') \
             not in node_tuple and (node.name, 'false') \
                  not in node_tuple]
        result = list()
        result.append(node_tuple)
        length = len(result)

        for node in lack_nodes:
            while length:
                length -= 1
                temp1 = result.pop(0).copy()
                temp2 = temp1.copy()
                
                temp1.append((node, 'true'))
                temp2.append((node, 'false'))
                
                result.append(temp1)
                result.append(temp2)
            length = len(result)
        return sum([self._compute_filled(tmp) for tmp in result])

    def _compute_filled(self, node_tuple):
        value = 1.0
        for name, val in node_tuple:
            node = self._search_node_by_name(name)
            temp = node.multi_parent(node_tuple)
            value *= temp
        return value

    def _search_node_by_name(self, name):
        for node in self.nodes:
            if node.name == name:
                return node

if __name__ == '__main__':
    b = BayesianNetwork('burglarnetwork.txt')
    b.compute_query('burglarqueries.txt')

