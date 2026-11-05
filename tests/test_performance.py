"""
Performance regression tests for the Markdown Decision Process project.
These tests benchmark core operations and track performance over time.
"""

import os
import sys
import timeit # Restored for TestScalability
import unittest # Restored for TestScalability
from pathlib import Path
import pytest
import numpy as np # Restored for TestScalability

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from mdp.document import Document
from mdp.markchain import MarkChain
from mdp.state_space import StateSpace
# from mdp.transformations import normalize_headings, SomeTransformation # Assuming SomeTransformation for example
# from mdp.quality import calculate_all_metrics # Assuming this for example
from mdp.policy_optimizer import PolicyOptimizer
from mdp.belief_updater import BeliefUpdater

# Helper function to generate markdown content
def generate_markdown_content(num_sections=10, num_paragraphs_per_section=5, num_subsections=3):
    content = [f"# Large Sample Document Generated for Benchmarking\n\n"]
    for i in range(1, num_sections + 1):
        content.append(f"## Section {i}\n\n")
        for j in range(1, num_paragraphs_per_section + 1):
            content.append(f"This is paragraph {j} in section {i}. {'Lorem ipsum dolor sit amet. ' * 10}\n\n")
        for k in range(1, num_subsections + 1):
            content.append(f"### Subsection {i}.{k}\n\n")
            content.append(f"This is content in subsection {i}.{k}. {'Consectetur adipiscing elit. ' * 8}\n\n")
    return "".join(content)

@pytest.mark.parametrize("sections,paragraphs,subsections", [(2, 2, 1), (3, 1, 2)])
def test_synthetic_markdown_has_intended_heading_and_paragraph_shape(
    sections, paragraphs, subsections
):
    content = generate_markdown_content(sections, paragraphs, subsections)
    document = Document(content=content)
    headings = document.get_headings()
    assert headings[0] == {
        "level": 1, "text": "Large Sample Document Generated for Benchmarking"
    }
    assert [h["text"] for h in headings if h["level"] == 2] == [
        f"Section {i}" for i in range(1, sections + 1)
    ]
    assert [h["text"] for h in headings if h["level"] == 3] == [
        f"Subsection {i}.{j}"
        for i in range(1, sections + 1)
        for j in range(1, subsections + 1)
    ]
    assert len(document.get_paragraphs()) == sections * (paragraphs + subsections)
    assert "\\n" not in content


@pytest.fixture(scope="session")
def sample_document_content():
    """Provide content for a moderately sized sample document."""
    return generate_markdown_content(num_sections=20, num_paragraphs_per_section=5, num_subsections=2)

@pytest.fixture(scope="session")
def large_document_content():
    """Provide content for a large sample document."""
    return generate_markdown_content(num_sections=100, num_paragraphs_per_section=10, num_subsections=5)

@pytest.fixture
def sample_document(sample_document_content):
    """Create a sample Document instance."""
    return Document(content=sample_document_content)

@pytest.fixture
def large_document(large_document_content):
    """Create a large Document instance."""
    return Document(content=large_document_content)

class TestPerformance:
    """Performance tests for MDP components using pytest-benchmark."""
    
    @pytest.mark.benchmark(group="document_creation")
    def test_document_creation(self, benchmark, sample_document_content):
        """Test performance of document creation."""
        benchmark(Document, content=sample_document_content)

    @pytest.mark.benchmark(group="document_parsing")
    def test_document_parsing_performance(self, benchmark, sample_document):
        """Test performance of parsing a document."""
        # Assuming Document.parse() is the method to benchmark.
        # If parsing happens at __init__, this might be similar to test_document_creation.
        # For this example, we call a presumed parse() method.
        # If no explicit parse method, one might benchmark re-initialization:
        # benchmark(lambda: Document(content=sample_document.content))
        try:
            benchmark(sample_document.parse)
        except AttributeError:
            # Fallback if .parse() doesn't exist, benchmark re-init
            benchmark(lambda: Document(content=sample_document.content))

    @pytest.mark.benchmark(group="document_structure")
    def test_document_structure(self, benchmark, sample_document):
        """Benchmark document structure extraction."""
        benchmark(sample_document.get_structure)

    @pytest.mark.benchmark(group="markchain_training")
    def test_markchain_training(self, benchmark, sample_document):
        """Measure one training call from an empty model in each timed round."""
        sampled_chains = []

        def setup_training():
            chain = MarkChain()
            sampled_chains.append(chain)
            return (chain, sample_document), {}

        benchmark.pedantic(
            MarkChain.train, setup=setup_training, rounds=5, iterations=1
        )
        assert sampled_chains and all(
            sum(chain.start_states.values()) == 1 for chain in sampled_chains
        )
        assert len({id(chain) for chain in sampled_chains}) == len(sampled_chains)
        assert all(
            chain.transitions == sampled_chains[0].transitions
            for chain in sampled_chains
        )

    @pytest.mark.benchmark(group="markchain_generation")
    def test_markchain_generation(self, benchmark, sample_document):
        """Benchmark MarkChain generation."""
        chain = MarkChain()
        chain.train(sample_document)
        start_state = next(iter(chain.states), None)
        if start_state:
            benchmark(chain.sample, start_state=start_state, length=100)
        else:
            pytest.skip("Cannot run MarkChain generation benchmark without states after training.")

    @pytest.mark.benchmark(group="state_space_generation")
    def test_state_space_generation(self, benchmark, sample_document):
        """Benchmark StateSpace creation."""
        benchmark(StateSpace, sample_document)

    @pytest.mark.benchmark(group="quality_metrics")
    def test_quality_metrics_performance(self, benchmark, sample_document):
        """Test performance of calculating quality metrics (placeholder)."""
        # from mdp.quality import calculate_all_metrics # Ensure this import exists if uncommented
        # benchmark(calculate_all_metrics, sample_document)
        pytest.skip("calculate_all_metrics function not yet implemented or imported")

    @pytest.mark.benchmark(group="document_modification")
    def test_document_modification_performance(self, benchmark, sample_document):
        """Measure one real mutation with fresh, untimed document setup."""
        sampled_documents = []
        expected_content = sample_document.content + "\n\nNew paragraph for benchmark"

        def setup_modification():
            document = Document(content=sample_document.content)
            sampled_documents.append(document)
            return (document, "New paragraph for benchmark", "paragraph"), {}

        benchmark.pedantic(
            Document.add_element, setup=setup_modification, rounds=5, iterations=1
        )
        assert sampled_documents and all(
            doc.content == expected_content for doc in sampled_documents
        )
        assert len({id(doc) for doc in sampled_documents}) == len(sampled_documents)

    @pytest.mark.benchmark(group="transformation_application")
    def test_transformation_application_performance(self, benchmark, sample_document):
        """Test performance of applying a transformation (placeholder)."""
        # from mdp.transformations import SomeTransformation # Ensure this import exists if uncommented
        # doc_copy = Document(content=sample_document.content)
        # transformation = SomeTransformation() # Replace with an actual Transformation
        # benchmark(transformation.apply, doc_copy)
        pytest.skip("SomeTransformation or its apply method not yet implemented or imported")

    @pytest.mark.benchmark(group="optimizer")
    def test_policy_optimizer(self, benchmark, sample_document):
        """Benchmark policy optimization."""
        state_space = StateSpace(sample_document)
        optimizer = PolicyOptimizer(state_space=state_space)
        # Benchmark value iteration instead since optimize_with_func requires file I/O
        benchmark(optimizer.value_iteration, max_iterations=10)

    @pytest.mark.benchmark(group="belief_updater")
    def test_belief_updater(self, benchmark, sample_document):
        """Measure one observation update from a fresh prior in each round."""
        observation = {"instruction": 0.7, "example": 0.3}
        sampled_updaters = []

        def setup_observation():
            updater = BeliefUpdater()
            sampled_updaters.append(updater)
            return (updater, observation), {}

        benchmark.pedantic(
            BeliefUpdater.update_from_observation,
            setup=setup_observation, rounds=5, iterations=1,
        )
        assert sampled_updaters and all(
            updater.observations == [observation] for updater in sampled_updaters
        )
        assert len({id(updater) for updater in sampled_updaters}) == len(
            sampled_updaters
        )
        assert all(
            updater.get_all_beliefs() == sampled_updaters[0].get_all_beliefs()
            for updater in sampled_updaters
        )

    @pytest.mark.benchmark(group="document_creation_scaling")
    def test_document_creation_scaling(self, benchmark, large_document_content):
        """Test scaling of document creation with larger input."""
        benchmark(Document, content=large_document_content)

    @pytest.mark.benchmark(group="document_parsing_scaling")
    def test_document_parsing_scaling(self, benchmark, large_document):
        """Test scaling of document parsing with larger input."""
        # Similar to non-scaling version, benchmark .parse() or re-init
        try:
            benchmark(large_document.parse)
        except AttributeError:
            benchmark(lambda: Document(content=large_document.content))

    @pytest.mark.benchmark(group="state_space_generation_scaling")
    def test_state_space_generation_scaling(self, benchmark, large_document):
        """Test scaling of state space generation with larger input."""
        benchmark(StateSpace, large_document)

    @pytest.mark.benchmark(group="quality_metrics_scaling")
    def test_quality_metrics_scaling(self, benchmark, large_document):
        """Test scaling of quality metrics with larger input (placeholder)."""
        # from mdp.quality import calculate_all_metrics # Ensure this import exists if uncommented
        # benchmark(calculate_all_metrics, large_document)
        pytest.skip("calculate_all_metrics function not yet implemented or imported")

    @pytest.mark.benchmark(group="transformation_application_scaling")
    def test_transformation_application_scaling(self, benchmark, large_document):
        """Test scaling of applying a transformation to a large document (placeholder)."""
        # from mdp.transformations import SomeTransformation # Ensure this import exists if uncommented
        # doc_copy = Document(content=large_document.content)
        # transformation = SomeTransformation() # Replace with an actual Transformation
        # benchmark(transformation.apply, doc_copy)
        pytest.skip("SomeTransformation or its apply method not yet implemented or imported")

    @pytest.mark.benchmark(group="transformations")
    def test_normalize_headings_performance(self, benchmark, sample_document):
        """Benchmark heading normalization (placeholder)."""
        pytest.skip("normalize_headings function not yet implemented or imported")

class TestScalability(unittest.TestCase):
    """Tests for component scalability."""
    
    def generate_markdown(self, num_paragraphs):
        """Generate markdown with the specified number of paragraphs."""
        content = ["# Scalability Test\n\n"]
        for i in range(num_paragraphs):
            content.append(f"This is paragraph {i+1}. " * 5)
            content.append("\n\n")
        return "".join(content)
    
    def test_document_scaling(self):
        """Test how document processing scales with document size."""
        sizes = [10, 50, 100, 500, 1000]
        times = []
        
        for size in sizes:
            content = self.generate_markdown(size)
            
            # Measure time to create document and extract structure
            start_time = timeit.default_timer()
            doc = Document(content)
            doc.get_structure()
            elapsed = timeit.default_timer() - start_time
            
            times.append(elapsed)
            print(f"Document size: {size} paragraphs, Time: {elapsed:.4f}s")
        
        # Calculate scaling factor
        if len(sizes) > 1 and len(times) > 1:
            log_sizes = np.log(sizes)
            log_times = np.log(times)
            
            # Linear regression to find scaling power
            n = len(sizes)
            slope = (n * np.sum(log_sizes * log_times) - np.sum(log_sizes) * np.sum(log_times)) / \
                    (n * np.sum(log_sizes ** 2) - np.sum(log_sizes) ** 2)
            
            print(f"Scaling factor: O(n^{slope:.2f})")
            self.assertLess(slope, 2.0, "Document processing should scale better than O(n²)")
    
    def test_markchain_scaling(self):
        """Test how MarkChain training scales with document size."""
        sizes = [10, 50, 100, 500]
        times = []
        
        for size in sizes:
            content = self.generate_markdown(size)
            doc = Document(content)
            chain = MarkChain()
            
            # Measure time to train
            start_time = timeit.default_timer()
            chain.train(doc)
            elapsed = timeit.default_timer() - start_time
            
            times.append(elapsed)
            print(f"Document size: {size} paragraphs, Training time: {elapsed:.4f}s")
        
        # Calculate scaling factor
        if len(sizes) > 1 and len(times) > 1:
            log_sizes = np.log(sizes)
            log_times = np.log(times)
            
            # Linear regression to find scaling power
            n = len(sizes)
            slope = (n * np.sum(log_sizes * log_times) - np.sum(log_sizes) * np.sum(log_times)) / \
                    (n * np.sum(log_sizes ** 2) - np.sum(log_sizes) ** 2)
            
            print(f"Scaling factor: O(n^{slope:.2f})")
            self.assertLess(slope, 2.5, "MarkChain training should scale reasonably")
    
    def test_state_space_scaling(self):
        """Test how StateSpace creation scales with document size."""
        sizes = [10, 50, 100, 200]
        times = []
        
        for size in sizes:
            content = self.generate_markdown(size)
            doc = Document(content)
            
            # Measure time to create state space
            start_time = timeit.default_timer()
            state_space = StateSpace(doc)
            elapsed = timeit.default_timer() - start_time
            
            times.append(elapsed)
            print(f"Document size: {size} paragraphs, StateSpace creation time: {elapsed:.4f}s")
        
        # Calculate scaling factor
        if len(sizes) > 1 and len(times) > 1:
            log_sizes = np.log(sizes)
            log_times = np.log(times)
            
            # Linear regression to find scaling power
            n = len(sizes)
            slope = (n * np.sum(log_sizes * log_times) - np.sum(log_sizes) * np.sum(log_times)) / \
                    (n * np.sum(log_sizes ** 2) - np.sum(log_sizes) ** 2)
            
            print(f"Scaling factor: O(n^{slope:.2f})")
            self.assertLess(slope, 3.0, "StateSpace creation should scale reasonably")

    def test_normalize_headings_performance(self):
        """Test heading normalization performance."""
        from mdp import normalize_headings
        doc = Document(content=self.generate_markdown(100))
        
        start_time = timeit.default_timer()
        result = normalize_headings(doc)
        elapsed = timeit.default_timer() - start_time
        
        print(f"Normalize headings time: {elapsed:.4f}s")
        self.assertIsNotNone(result)
        self.assertLess(elapsed, 1.0, "Normalize headings should complete in under 1 second")

    def test_complex_transformation_performance(self):
        """Test complex transformation pipeline performance."""
        from mdp import TransformationPipeline, HeadingLevelTransformation, ListFormatTransformation
        import tempfile
        
        doc = Document(content=self.generate_markdown(100))
        pipeline = TransformationPipeline([
            HeadingLevelTransformation(1),
            ListFormatTransformation("unordered")
        ])
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            start_time = timeit.default_timer()
            pipeline.apply(doc, tmp_path)
            elapsed = timeit.default_timer() - start_time
            
            print(f"Complex transformation time: {elapsed:.4f}s")
            self.assertLess(elapsed, 2.0, "Complex transformation should complete in under 2 seconds")
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_normalize_headings_scaling(self):
        """Test heading normalization scaling."""
        from mdp import normalize_headings
        sizes = [50, 100, 200]
        times = []
        
        for size in sizes:
            doc = Document(content=self.generate_markdown(size))
            start_time = timeit.default_timer()
            normalize_headings(doc)
            elapsed = timeit.default_timer() - start_time
            times.append(elapsed)
            print(f"Size: {size}, Time: {elapsed:.4f}s")
        
        # Verify reasonable scaling
        if len(times) > 1:
            self.assertLess(times[-1] / times[0], 10.0, "Scaling should be reasonable")

if __name__ == '__main__':
    unittest.main() 