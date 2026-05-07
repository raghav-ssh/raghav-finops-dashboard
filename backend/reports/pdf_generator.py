"""
PDF report generation utilities with professional design.
"""
from pathlib import Path
from typing import List, Tuple
from datetime import date, datetime

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas

from core.logger import setup_logger


logger = setup_logger(__name__)


class PDFReportGenerator:
    """Generate professional, beautiful PDF reports for cost analysis."""
    
    # Professional color palette
    COLORS = {
        'primary': colors.HexColor('#2563eb'),      # Blue
        'secondary': colors.HexColor('#7c3aed'),    # Purple
        'success': colors.HexColor('#10b981'),      # Green
        'warning': colors.HexColor('#f59e0b'),      # Orange
        'danger': colors.HexColor('#ef4444'),       # Red
        'dark': colors.HexColor('#1f2937'),         # Dark gray
        'text': colors.HexColor('#374151'),         # Text gray
        'light_gray': colors.HexColor('#f3f4f6'),   # Light gray
        'border': colors.HexColor('#e5e7eb'),       # Border gray
        'white': colors.white,
        'header_bg': colors.HexColor('#f9fafb'),    # Very light gray
    }
    
    def __init__(self, output_path: Path):
        """
        Initialize PDF generator with professional styling.
        
        Args:
            output_path: Path for output PDF file
        """
        self.output_path = output_path
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            leftMargin=0.75 * inch,
            rightMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch
        )
        
        self.story = []
        self.styles = self._create_styles()
        
        logger.info(f"PDF generator initialized: {output_path}")
    
    def _create_styles(self) -> dict:
        """Create custom paragraph styles with professional design."""
        base_styles = getSampleStyleSheet()
        
        custom_styles = {
            'title': ParagraphStyle(
                'CustomTitle',
                parent=base_styles['Title'],
                fontSize=28,
                textColor=self.COLORS['primary'],
                alignment=TA_CENTER,
                spaceAfter=10,
                fontName='Helvetica-Bold',
                leading=34
            ),
            'subtitle': ParagraphStyle(
                'CustomSubtitle',
                parent=base_styles['Normal'],
                fontSize=12,
                textColor=self.COLORS['text'],
                alignment=TA_CENTER,
                spaceAfter=30,
                fontName='Helvetica'
            ),
            'heading': ParagraphStyle(
                'CustomHeading',
                parent=base_styles['Heading1'],
                fontSize=18,
                textColor=self.COLORS['primary'],
                spaceBefore=24,
                spaceAfter=12,
                fontName='Helvetica-Bold',
                borderWidth=0,
                borderPadding=0,
                leftIndent=0,
                borderColor=self.COLORS['primary'],
                borderRadius=0
            ),
            'subheading': ParagraphStyle(
                'CustomSubheading',
                parent=base_styles['Heading2'],
                fontSize=14,
                textColor=self.COLORS['secondary'],
                spaceBefore=16,
                spaceAfter=8,
                fontName='Helvetica-Bold'
            ),
            'body': ParagraphStyle(
                'CustomBody',
                parent=base_styles['Normal'],
                fontSize=10,
                leading=14,
                textColor=self.COLORS['text'],
                fontName='Helvetica'
            ),
            'body_bold': ParagraphStyle(
                'CustomBodyBold',
                parent=base_styles['Normal'],
                fontSize=10,
                leading=14,
                textColor=self.COLORS['dark'],
                fontName='Helvetica-Bold'
            ),
            'small': ParagraphStyle(
                'CustomSmall',
                parent=base_styles['Normal'],
                fontSize=9,
                leading=12,
                textColor=self.COLORS['text'],
                fontName='Helvetica'
            )
        }
        
        return custom_styles
    
    def add_cover_page(self, title: str, subtitle: str, date_str: str):
        """Add a professional cover page."""
        # Add some space from top
        self.story.append(Spacer(1, 2 * inch))
        
        # Title
        self.story.append(Paragraph(title, self.styles['title']))
        
        # Subtitle
        self.story.append(Paragraph(subtitle, self.styles['subtitle']))
        
        # Date box
        date_style = ParagraphStyle(
            'DateStyle',
            parent=self.styles['body'],
            alignment=TA_CENTER,
            fontSize=11,
            textColor=self.COLORS['text']
        )
        self.story.append(Paragraph(f"<b>Report Date:</b> {date_str}", date_style))
        self.story.append(Spacer(1, 0.1 * inch))
        self.story.append(Paragraph(
            f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
            date_style
        ))
        
        self.story.append(PageBreak())
    
    def add_title(self, title: str):
        """Add report title."""
        self.story.append(Paragraph(title, self.styles['title']))
        self.story.append(Spacer(1, 0.2 * inch))
    
    def add_heading(self, text: str):
        """Add section heading with underline."""
        self.story.append(Spacer(1, 0.1 * inch))
        self.story.append(Paragraph(text, self.styles['heading']))
        # Add a colored line under heading
        line_table = Table([['']], colWidths=[7 * inch])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, self.COLORS['primary']),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        self.story.append(line_table)
        self.story.append(Spacer(1, 0.1 * inch))
    
    def add_subheading(self, text: str):
        """Add subsection heading."""
        self.story.append(Paragraph(text, self.styles['subheading']))
    
    def add_paragraph(self, text: str, style='body'):
        """Add body paragraph."""
        self.story.append(Paragraph(text, self.styles[style]))
        self.story.append(Spacer(1, 0.08 * inch))
    
    def add_spacer(self, height: float = 0.2):
        """Add vertical space."""
        self.story.append(Spacer(1, height * inch))
    
    def add_page_break(self):
        """Add page break."""
        self.story.append(PageBreak())
    
    def add_summary_table(self, data: List[Tuple[str, str]]):
        """
        Add a styled summary table with professional design.
        
        Args:
            data: List of (label, value) tuples
        """
        table = Table(data, colWidths=[3.5 * inch, 3.5 * inch])
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.COLORS['white']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), self.COLORS['white']),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.COLORS['text']),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            
            # Borders
            ('BOX', (0, 0), (-1, -1), 1, self.COLORS['border']),
            ('LINEBELOW', (0, 0), (-1, 0), 2, self.COLORS['primary']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.COLORS['white'], self.COLORS['header_bg']]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3 * inch))
    
    def add_data_table(self, df: pd.DataFrame, max_rows: int = 50):
        """
        Add a professional data table from DataFrame.
        
        Args:
            df: DataFrame to display
            max_rows: Maximum rows to include
        """
        # Limit rows
        display_df = df.head(max_rows).copy()
        
        # Format numeric columns
        for col in display_df.columns:
            if pd.api.types.is_numeric_dtype(display_df[col]):
                display_df[col] = display_df[col].apply(
                    lambda x: f"{x:,.2f}" if pd.notna(x) else ""
                )
        
        # Prepare table data
        table_data = [display_df.columns.tolist()] + display_df.values.tolist()
        
        # Calculate column widths dynamically
        num_cols = len(display_df.columns)
        col_width = 7 * inch / num_cols
        
        # Create table
        table = Table(table_data, colWidths=[col_width] * num_cols)
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.COLORS['white']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), self.COLORS['white']),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.COLORS['text']),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            
            # Borders and styling
            ('BOX', (0, 0), (-1, -1), 0.5, self.COLORS['border']),
            ('LINEBELOW', (0, 0), (-1, 0), 2, self.COLORS['primary']),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, self.COLORS['border']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.COLORS['white'], self.COLORS['header_bg']]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.2 * inch))
    
    def add_info_box(self, text: str, box_type: str = 'info'):
        """
        Add an information box with colored border.
        
        Args:
            text: Text content
            box_type: 'info', 'success', 'warning', or 'danger'
        """
        color_map = {
            'info': self.COLORS['primary'],
            'success': self.COLORS['success'],
            'warning': self.COLORS['warning'],
            'danger': self.COLORS['danger']
        }
        
        box_color = color_map.get(box_type, self.COLORS['primary'])
        
        # Create a table for the box
        box_table = Table([[Paragraph(text, self.styles['body'])]], colWidths=[6.5 * inch])
        box_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['header_bg']),
            ('BOX', (0, 0), (-1, -1), 2, box_color),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.story.append(box_table)
        self.story.append(Spacer(1, 0.15 * inch))
    
    def add_image(self, image_path: Path, max_width: float = 6.5):
        """
        Add an image to the report with border.
        
        Args:
            image_path: Path to image file
            max_width: Maximum image width in inches
        """
        if image_path.exists():
            try:
                img_reader = ImageReader(str(image_path))
                iw, ih = img_reader.getSize()
                aspect = ih / float(iw)
                
                # Calculate dimensions
                img_width = max_width * inch
                img_height = img_width * aspect
                
                # Limit height
                if img_height > 5 * inch:
                    img_height = 5 * inch
                    img_width = img_height / aspect
                
                # Create image with border
                img = Image(str(image_path), width=img_width, height=img_height)
                
                # Wrap in table for border
                img_table = Table([[img]], colWidths=[img_width + 0.2 * inch])
                img_table.setStyle(TableStyle([
                    ('BOX', (0, 0), (-1, -1), 1, self.COLORS['border']),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['white']),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ]))
                
                self.story.append(img_table)
                self.story.append(Spacer(1, 0.2 * inch))
            except Exception as e:
                logger.warning(f"Error adding image {image_path}: {e}")
        else:
            logger.warning(f"Image not found: {image_path}")
    
    def _draw_header_footer(self, canvas_obj, doc):
        """Draw header and footer on each page."""
        canvas_obj.saveState()
        
        # Footer
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(self.COLORS['text'])
        
        # Page number
        page_num = canvas_obj.getPageNumber()
        text = f"Page {page_num}"
        canvas_obj.drawRightString(A4[0] - 0.75 * inch, 0.5 * inch, text)
        
        # Footer line
        canvas_obj.setStrokeColor(self.COLORS['border'])
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(0.75 * inch, 0.65 * inch, A4[0] - 0.75 * inch, 0.65 * inch)
        
        # Company/Report name
        canvas_obj.drawString(0.75 * inch, 0.5 * inch, "FinOps Cost Report")
        
        canvas_obj.restoreState()

    def build(self):
        """Build and save the PDF document."""
        try:
            self.doc.build(
                self.story,
                onFirstPage=self._draw_header_footer,
                onLaterPages=self._draw_header_footer
            )
            logger.info(f"PDF report generated: {self.output_path}")
        except Exception as e:
            logger.error(f"Error building PDF: {e}")
            raise
