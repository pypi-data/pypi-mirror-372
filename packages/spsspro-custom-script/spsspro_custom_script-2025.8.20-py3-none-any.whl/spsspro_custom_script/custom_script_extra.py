import base64
import io
from typing import Optional


class NotebookViewExtra:
    func_method = [
        "_repr_html_", "_repr_svg_", "_repr_latex_", "_repr_png_", "__str__", "__repr__"
    ]

    @staticmethod
    def dataframe_to_html(obj) -> Optional[str]:
        if hasattr(obj, '_repr_html_'):
            extra_css = """
                                <style>
                                .dataframe {
                                    border-collapse: collapse;
                                    font-family: monospace;
                                    font-size: 13px;
                                    width: 100%;
                                    display: block;
                                    overflow-x: auto;
                                }

                                .dataframe th,
                                .dataframe td {
                                    border: 1px solid #ccc;
                                    padding: 6px 12px;
                                    white-space: nowrap;
                                }

                                .dataframe thead {
                                    background-color: #f2f2f2;
                                }

                                .dataframe tbody tr:nth-child(even) {
                                    background-color: #f9f9f9;
                                }
                                </style>
                                """
            return extra_css + obj._repr_html_()
        return None

    @staticmethod
    def figure_to_html(fig, format='png') -> Optional[str]:
        buf = io.BytesIO()
        fig.savefig(buf, format=format)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        html = f'<div><img src="data:image/png;base64,{img_base64}" /></div>'

        return html

    @staticmethod
    def hiplot_to_html(obj) -> Optional[str]:
        from bs4 import BeautifulSoup
        full_html = obj.to_html()

        soup = BeautifulSoup(full_html, 'html.parser')
        # 提取 body 内部所有内容
        body_inner_html = soup.body.decode_contents()

        return body_inner_html

    @staticmethod
    def smiles_to_2d_html(obj, width: float = 500, height: float = 500):
        from rdkit.Chem import Draw
        img = Draw.MolToImage(obj, size=(width, height))

        return NotebookViewExtra.PngImageFile_to_html(img)

    @staticmethod
    def smiles_to_3d_html(obj, width: float = 500, height: float = 500):
        import py3Dmol
        viewer = py3Dmol.view(width=width, height=height)
        viewer.addModel(obj, 'mol')
        viewer.setStyle({'stick': {}})
        viewer.setBackgroundColor('white')
        viewer.zoomTo()

        return viewer._make_html()

    @staticmethod
    def py3Dmol_to_html(obj) -> Optional[str]:
        return obj._make_html()

    @staticmethod
    def PngImageFile_to_html(obj):
        buf = io.BytesIO()

        obj.save(buf, format='PNG')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        html = f'<div><img src="data:image/png;base64,{img_base64}" /></div>'

        return html
