import pandas as pd
import pytest
from generate_html_report import add_tree_prefixes

@pytest.fixture
def sample_data():
    """Provides a sample DataFrame to test tree generation logic."""
    data = {
        'Indent': [
            0,  # 0: root1
            1,  # 1: child of root1
            2,  # 2: child of child1
            1,  # 3: last child of root1
            0,  # 4: root2
            1,  # 5: child of root2
            1,  # 6: child of root2
            2,  # 7: child of child2
            2,  # 8: last child of child2
            1,  # 9: last child of root2
            0   # 10: last root
        ],
        'Element/Attribute Name': [
            'root1',
            'child1.1',
            'child1.1.1',
            'child1.2',
            'root2',
            'child2.1',
            'child2.2',
            'child2.2.1',
            'child2.2.2',
            'child2.3',
            'root3'
        ]
    }
    return pd.DataFrame(data)

def test_tree_prefix_generation(sample_data):
    """Tests that the tree prefixes are generated correctly."""
    # Expected prefixes for the sample_data, now corrected.
    expected_prefixes = [
        '',           # 0: root1
        '├─ ',        # 1: child1.1
        '│   └─ ',    # 2: child1.1.1
        '└─ ',        # 3: child1.2
        '',           # 4: root2
        '├─ ',        # 5: child2.1
        '├─ ',        # 6: child2.2
        '│   ├─ ',    # 7: child2.2.1
        '│   └─ ',    # 8: child2.2.2
        '└─ ',        # 9: child2.3
        ''            # 10: root3
    ]

    # Run the function
    result_df = add_tree_prefixes(sample_data)

    # Check if the generated prefixes match the expected ones
    assert result_df['TreePrefix'].tolist() == expected_prefixes
