import os
import subprocess
from docutils import nodes
from sphinx import addnodes
import sphinx.util.compat
from docutils.transforms import Transform
from docutils import utils

def format_dot(dot_fp, pdf_fp, png_fp):
    returncode = subprocess.check_call(
        args=[
            'dot',
            '-Tpdf',
            ],
        stdin=dot_fp,
        stdout=pdf_fp,
        close_fds=True,
        )

    pdf_fp.seek(0)
    returncode = subprocess.check_call(
        args=[
            'convert',
            '-resize', '600x600>',
            'pdf:-',
            'png:-',
            ],
        stdin=pdf_fp,
        stdout=png_fp,
        close_fds=True,
        )

class DotAsImage(Transform):
    default_priority = 400

    def apply(self, **kwargs):
        for node in self.document.traverse(
            condition=nodes.image,
            ):
            uri = node['uri']
            base, ext = os.path.splitext(uri)
            if ext != '.dot':
                continue
            source = self.document['source']
            source_rel = utils.relative_path(None, source)
            source_dir = os.path.dirname(source_rel)
            uri_from_root = os.path.join(source_dir, uri)

            png_uri = '%s.png' % base
            base_from_root, _ = os.path.splitext(uri_from_root)
            png_path = '%s.png' % base_from_root

            # TODO would like to use sphinx.ext.graphviz.render_dot,
            # but it wants an object as self.

            with file(uri_from_root) as dot_fp:
                with file(png_path, 'w') as png_fp:
                    with os.tmpfile() as pdf_fp:
                        format_dot(
                            dot_fp=dot_fp,
                            pdf_fp=pdf_fp,
                            png_fp=png_fp,
                            )

            node['uri'] = png_uri

def setup(Sphinx):
    Sphinx.add_transform(DotAsImage)
