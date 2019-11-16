import os
from uuid import uuid4

import pytest

from benchlingapi.exceptions import BenchlingAPIException


class TestDNAAlignment:
    @pytest.fixture(scope="module")
    def make_temporary_sequences(self, session, trash_folder):
        """Create a temporary sequence and then archive it."""
        seq_arr = []

        def temp(sequences):
            for seq_str in sequences:
                seq_arr.append(
                    session.DNASequence(
                        bases=seq_str,
                        name=str(uuid4()),
                        folder_id=trash_folder.id,
                        is_circular=False,
                    )
                )
            for seq in seq_arr:
                seq.save()

            return seq_arr

        yield temp

        for seq in seq_arr:
            seq.archive()

    @pytest.mark.parametrize(
        "do_delete", [False, True], ids=["keep alignment", "delete alignment"]
    )
    def test_alignment_with_other_sequences(
        self, session, make_temporary_sequences, do_delete
    ):
        """This tests that sequences are valid inputs."""
        dnas = make_temporary_sequences(
            [
                "actccaattggtgatggtccagtcttgttaccagacaaccattacttatccactcaatctgccttatcc"
                "aaagatccaaacgaaaagagagaccacatggtcttgttagaatttgttactgctgctggtattac",
                "aattggtgatggtccagtactccaattggtgatggtccagtcttgttaccagacaaccattacttatcc"
                "actcaatctgccttatccaaagatccaaacgaaaagagagaccacatggtcttgttagaatttgttact"
                "gctgctggtattac",
                "aattggtgatggtccagtactccaattggtgatggtccagtcttgttaccagacaaccattacttatcc"
                "actcaatctgcctAAAAAAAtatccaaagatccaaacgaaaagagagaccacatggtcttgttagaatttgttact"
                "gctgctggtattacAGGGAGGGAGGAGAGGA",
            ]
        )

        for dna in dnas:
            print(dna.name)

        template = dnas[0]
        other = dnas[1:]
        task = session.DNAAlignment.submit_alignment(
            algorithm="mafft",
            name="my new alignment",
            template=template,
            filepaths=[],
            sequences=other,
        )

        task.wait()
        assert task.status == "SUCCEEDED"
        if do_delete:
            alignment = task.response_class
            alignment.delete()

    def test_alignment_with_mixed_files_seqids_and_seqs(
        self, session, make_temporary_sequences
    ):
        """This tests that sequence ids, DNASequence, and filepaths are all
        valid inputs for the alignment submission method."""
        dnas = make_temporary_sequences(
            [
                "actccaattggtgatggtccagtcttgttaccagacaaccattacttatccactcaatctgccttatcc"
                "aaagatccaaacgaaaagagagaccacatggtcttgttagaatttgttactgctgctggtattac",
                "aattggtgatggtccagtactccaattggtgatggtccagtcttgttaccagacaaccattacttatcc"
                "actcaatctgccttatccaaagatccaaacgaaaagagagaccacatggtcttgttagaatttgttact"
                "gctgctggtattac",
                "aattggtgatggtccagtactccaattggtgatggtccagtcttgttaccagacaaccattacttatcc"
                "actcaatctgcctAAAAAAAtatccaaagatccaaacgaaaagagagaccacatggtcttgttagaatttgttact"
                "gctgctggtattacAGGGAGGGAGGAGAGGA",
            ]
        )

        here = os.path.abspath(os.path.dirname(__file__))
        filepath = os.path.join(here, "424889-14889.ab1")

        template = dnas[0]
        others = [dnas[1], dnas[2].id]
        task = session.DNAAlignment.submit_alignment(
            algorithm="mafft",
            name="my new alignment",
            template=template,
            filepaths=[filepath],
            sequences=others,
        )

        task.wait()
        print(task)
        assert task.status == "SUCCEEDED"

    def test_alignment_with_ab1_files(self, session, make_temporary_sequences):
        """This tests that filepaths are valid inputs for the alignment
        submission method."""
        dnas = make_temporary_sequences(
            [
                "actccaattggtgatggtccagtcttgttaccagacaaccattacttatccactcaatctgccttatcc"
                "aaagatccaaacgaaaagagagaccacatggtcttgttagaatttgttactgctgctggtattac"
            ]
        )

        here = os.path.abspath(os.path.dirname(__file__))
        filepath = os.path.join(here, "424889-14889.ab1")

        template = dnas[0]
        task = session.DNAAlignment.submit_alignment(
            algorithm="mafft",
            name="my new alignment",
            template=template,
            filepaths=[filepath],
        )

        task.wait()
        print(task)
        print(dnas[0].id)

        print(template.web_url)
        assert task.status == "SUCCEEDED"

    def test_wrong_algorithm(self, session, make_temporary_sequences):
        dnas = make_temporary_sequences(
            [
                "actccaattggtgatggtccagtcttgttaccagacaaccattacttatccactcaatctgccttatcc"
                "aaagatccaaacgaaaagagagaccacatggtcttgttagaatttgttactgctgctggtattac",
                "aattggtgatggtccagtactccaattggtgatggtccagtcttgttaccagacaaccattacttatcc"
                "actcaatctgccttatccaaagatccaaacgaaaagagagaccacatggtcttgttagaatttgttact"
                "gctgctggtattac",
                "aattggtgatggtccagtactccaattggtgatggtccagtcttgttaccagacaaccattacttatcc"
                "actcaatctgcctAAAAAAAtatccaaagatccaaacgaaaagagagaccacatggtcttgttagaatttgttact"
                "gctgctggtattacAGGGAGGGAGGAGAGGA",
            ]
        )

        for dna in dnas:
            print(dna.name)

        template = dnas[0]
        other = dnas[1:]
        with pytest.raises(BenchlingAPIException):
            session.DNAAlignment.submit_alignment(
                algorithm="not_an_algorithm",
                name="my new alignment",
                template=template,
                filepaths=[],
                sequences=other,
            )
