from ipamd.public.utils.output import error
from ipamd.public.models.sequence import *
from ipamd.public.utils.plugin_manager import PluginBase
from ipamd.public import shared_data

class Sakuanna(PluginBase):
    def __init__(self, app):
        extra_plugin_dir = config.get('simulation_plugin_dir')
        plugin_dir = ([
                          shared_data.module_installation_dir + '/plugins/sakuanna',
                      ] + extra_plugin_dir)
        super().__init__(plugin_dir)
        self.load_all()
        self.app = app

    @staticmethod
    def __read_fasta(fasta_path):
        seq_entry_list = []
        try:
            with open(fasta_path, 'r') as file:
                lines = file.readlines()
                name = ''
                seq = ''
                for line in lines:
                    if not line.strip():
                        continue
                    if line.startswith('>'):
                        if name != '' and seq != '':
                            seq_entry_list.append((name, seq))
                            seq = ''
                        name = line[1:].strip()
                    else:
                        if name == '':
                            error("FASTA file does not start with a header line.")
                            raise ValueError()
                        seq += line.strip()
                if name != '' and seq != '':
                    seq_entry_list.append((name, seq))
                return seq_entry_list

        except FileNotFoundError:
            error(f"File {fasta_path} not found.")
            raise
        except Exception as e:
            error(f"An error occurred while reading the FASTA file: {e}")
            raise

    def new_protein_sequence(self, fasta_path=None, name=None, sequence=None):
        protein_sequence_list = []
        if fasta_path is not None:
            seq_entry_list = self.__read_fasta(fasta_path)
            for seq_entry in seq_entry_list:
                name, sequence = seq_entry
                protein_sequence_list.append(ProteinSequence(name, sequence))
        elif name is not None and sequence is not None:
            protein_sequence_list.append(ProteinSequence(name, sequence))
        else:
            error("Either fasta_path or both name and sequence must be provided.")
            raise ValueError()
        if len(protein_sequence_list) == 1:
            return protein_sequence_list[0]
        else:
            return tuple(protein_sequence_list)

    def new_dna_sequence(self, fasta_path, name, sequence):
        if fasta_path is None:
            name, sequence = self.__read_fasta(fasta_path)
        return DNASequence(name, sequence)

    def new_rna_sequence(self, fasta_path, name, sequence):
        if fasta_path is None:
            name, sequence = self.__read_fasta(fasta_path)
        return RNASequence(name, sequence)
