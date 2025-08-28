# CellTypeTree
Single-Cell RNA-Seq label harmonization and aggregation on a tree of cell types.

<img src="https://github.com/lorenzoamir/celltypetree/blob/main/docs/logo/celltypetree.png?raw=true" alt="Image" width="220" align="left" style="margin-right: 15px;"/>

<p>
Automatic tools for cell type annotation vary in resolution, coverage, and accuracy—making it hard to choose the best one upfront. Combining multiple annotation sources can facilitate unsupervised cell type annotations, but also brings a set of recurring conflicts:
</p>

<ul>
  <li>The same cell type is referred to by multiple names (e.g. <em>NK cells</em> vs <em>NK</em>)</li>
  <li>Annotations have different resolutions (e.g. <em>Monocytes</em> vs <em>CD14 Mono</em>)</li>
  <li>The same cell gets assigned to different cell types (e.g. <em>Neutrophils</em> vs <em>Monocytes</em>)</li>
</ul>

<p>
<strong>CellTypeTree</strong> addresses this by mapping all labels onto a unified tree of cell types. Synonyms are linked to the same node (e.g. <em>NK cells</em> = <em>NK</em>), while parent-child links capture hierarchical relations (<em>CD14 Mono</em> ∈ <em>Monocytes</em>). When paths diverge (e.g. <em>Neutrophils</em> vs <em>Monocytes</em>), the final assignment is guided by label aggregation methods like majority voting.
</p>

## Installation

CellTypeTree is currently available on pypi test repository. To install (including all optional dependencies) run:
```{bash}
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple "celltypetree[all]"
```
