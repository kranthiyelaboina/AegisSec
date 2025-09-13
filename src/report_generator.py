"""
Report Generator for AegisSec
Generates comprehensive, user-friendly reports from penetration testing results
Developed by RunTime Terrors
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from jinja2 import Template

from config_manager import ConfigManager
from deepseek_client import DeepSeekClient

class ReportGenerator:
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.deepseek = DeepSeekClient(config_manager)  # Pass config manager
        self.reports_dir = Path(__file__).parent.parent / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Report templates
        self.html_template = self._get_html_template()
        self.markdown_template = self._get_markdown_template()
    
    def generate_report(self, session_data: Dict[str, Any], criteria: str, 
                       formats: List[str] = None) -> Optional[str]:
        """Generate reports in specified formats"""
        if formats is None:
            formats = ["html", "markdown"]  # Default formats
        
        session_id = session_data.get("session_id", "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate AI summary
        ai_summary = self.deepseek.generate_executive_summary(session_data)
        
        # Prepare report data
        report_data = self._prepare_report_data(session_data, ai_summary)
        
        generated_files = []
        
        for format_type in formats:
            if format_type == "html":
                file_path = self._generate_html_report(report_data, session_id, timestamp)
            elif format_type == "markdown":
                file_path = self._generate_markdown_report(report_data, session_id, timestamp)
            elif format_type == "pdf" and REPORTLAB_AVAILABLE:
                file_path = self._generate_pdf_report(report_data, session_id, timestamp)
            elif format_type == "json":
                file_path = self._generate_json_report(report_data, session_id, timestamp)
            else:
                logging.warning(f"Unsupported report format: {format_type}")
                continue
            
            if file_path:
                generated_files.append(file_path)
        
        return generated_files[0] if generated_files else None
    
    def generate_comprehensive_report(self, session_data: Dict[str, Any], criteria: str, 
                                    formats: List[str] = None) -> Optional[str]:
        """Generate comprehensive user-friendly reports with enhanced readability"""
        if formats is None:
            formats = ["html", "markdown"]
        
        session_id = session_data.get("session_id", "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate enhanced AI summary
        executive_summary = self.deepseek.generate_executive_summary(session_data)
        
        # Prepare enhanced report data
        report_data = self._prepare_comprehensive_report_data(session_data, executive_summary)
        
        generated_files = []
        
        for format_type in formats:
            if format_type == "html":
                file_path = self._generate_enhanced_html_report(report_data, session_id, timestamp)
            elif format_type == "markdown":
                file_path = self._generate_enhanced_markdown_report(report_data, session_id, timestamp)
            elif format_type == "pdf" and REPORTLAB_AVAILABLE:
                file_path = self._generate_enhanced_pdf_report(report_data, session_id, timestamp)
            elif format_type == "json":
                file_path = self._generate_json_report(report_data, session_id, timestamp)
            else:
                logging.warning(f"Unsupported report format: {format_type}")
                continue
            
            if file_path:
                generated_files.append(file_path)
        
        return generated_files[0] if generated_files else None
    
    def _prepare_comprehensive_report_data(self, session_data: Dict[str, Any], executive_summary: str = None) -> Dict[str, Any]:
        """Prepare enhanced data for comprehensive user-friendly reports"""
        results = session_data.get("results", {})
        intelligence_log = session_data.get("intelligence_log", [])
        
        # Enhanced statistics
        total_tools = len(results)
        successful_tools = sum(1 for r in results.values() if r.get("success", False))
        failed_tools = total_tools - successful_tools
        
        # Intelligence metrics
        adaptive_commands = sum(1 for entry in intelligence_log if entry.get("action") == "adaptive_command_generation")
        ai_interactions = len(intelligence_log)
        
        # Enhanced findings analysis
        all_findings = []
        findings_by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        risk_categories = {"network": 0, "web": 0, "authentication": 0, "configuration": 0, "other": 0}
        
        for tool_name, tool_result in results.items():
            analysis = tool_result.get("analysis", {})
            if analysis and "findings" in analysis:
                for finding in analysis["findings"]:
                    finding["tool"] = tool_name
                    finding["readable_description"] = self._make_finding_readable(finding)
                    all_findings.append(finding)
                    
                    severity = finding.get("severity", "low").lower()
                    if severity in findings_by_severity:
                        findings_by_severity[severity] += 1
                    
                    # Categorize by risk type
                    finding_type = finding.get("type", "").lower()
                    if any(term in finding_type for term in ["port", "service", "network"]):
                        risk_categories["network"] += 1
                    elif any(term in finding_type for term in ["web", "http", "ssl", "certificate"]):
                        risk_categories["web"] += 1
                    elif any(term in finding_type for term in ["auth", "login", "password", "credential"]):
                        risk_categories["authentication"] += 1
                    elif any(term in finding_type for term in ["config", "version", "header"]):
                        risk_categories["configuration"] += 1
                    else:
                        risk_categories["other"] += 1
        
        # Sort findings by severity and impact
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        all_findings.sort(key=lambda x: severity_order.get(x.get("severity", "low").lower(), 3))
        
        # Calculate security score
        security_score = self._calculate_security_score(findings_by_severity)
        
        # Generate recommendations
        priority_actions = self._generate_priority_actions(all_findings[:5])  # Top 5 issues
        
        return {
            "session_id": session_data.get("session_id", "Unknown"),
            "timestamp": session_data.get("timestamp", datetime.now().isoformat()),
            "criteria": session_data.get("criteria", "No criteria specified"),
            "executive_summary": executive_summary or "No executive summary available",
            "security_score": security_score,
            "statistics": {
                "total_tools": total_tools,
                "successful_tools": successful_tools,
                "failed_tools": failed_tools,
                "success_rate": round((successful_tools / total_tools * 100) if total_tools > 0 else 0, 1),
                "total_findings": len(all_findings),
                "findings_by_severity": findings_by_severity,
                "risk_categories": risk_categories,
                "intelligence_metrics": {
                    "adaptive_commands": adaptive_commands,
                    "ai_interactions": ai_interactions,
                    "intelligent_execution": adaptive_commands > 0
                }
            },
            "findings": all_findings,
            "priority_findings": all_findings[:10],  # Top 10 most critical
            "priority_actions": priority_actions,
            "tool_results": results,
            "intelligence_log": intelligence_log,
            "generation_time": datetime.now().isoformat(),
            "report_metadata": {
                "tool_name": "AegisSec",
                "developed_by": "RunTime Terrors",
                "report_version": "2.0",
                "user_friendly": True
            }
        }
    
    def _make_finding_readable(self, finding: Dict) -> str:
        """Convert technical finding into user-friendly description"""
        severity = finding.get("severity", "low").title()
        finding_type = finding.get("type", "Security Issue").title()
        details = finding.get("details", "No details available")
        
        # Create readable description
        if "port" in finding_type.lower():
            return f"Network port {details.split()[-1] if details else 'unknown'} is accessible from the internet"
        elif "version" in finding_type.lower():
            return f"Software version information is exposed: {details[:100]}"
        elif "ssl" in finding_type.lower() or "certificate" in finding_type.lower():
            return f"Website security certificate issue: {details[:100]}"
        elif "header" in finding_type.lower():
            return f"Web server configuration reveals: {details[:100]}"
        else:
            return f"{finding_type}: {details[:150]}"
    
    def _calculate_security_score(self, findings_by_severity: Dict) -> Dict:
        """Calculate overall security score and rating"""
        critical = findings_by_severity.get("critical", 0)
        high = findings_by_severity.get("high", 0)
        medium = findings_by_severity.get("medium", 0)
        low = findings_by_severity.get("low", 0)
        
        # Weighted scoring
        score = max(0, 100 - (critical * 25) - (high * 15) - (medium * 5) - (low * 1))
        
        if score >= 90:
            rating = "Excellent"
            color = "green"
        elif score >= 75:
            rating = "Good"
            color = "blue"
        elif score >= 60:
            rating = "Fair"
            color = "yellow"
        elif score >= 40:
            rating = "Poor"
            color = "orange"
        else:
            rating = "Critical"
            color = "red"
        
        return {
            "score": score,
            "rating": rating,
            "color": color,
            "description": self._get_score_description(score)
        }
    
    def _get_score_description(self, score: int) -> str:
        """Get user-friendly description of security score"""
        if score >= 90:
            return "Your security posture is excellent with minimal vulnerabilities found."
        elif score >= 75:
            return "Good security posture with some minor issues that should be addressed."
        elif score >= 60:
            return "Acceptable security with several issues requiring attention."
        elif score >= 40:
            return "Poor security posture with significant vulnerabilities that need immediate attention."
        else:
            return "Critical security issues found that require immediate remediation."
    
    def _generate_priority_actions(self, top_findings: List[Dict]) -> List[Dict]:
        """Generate priority actions for top findings"""
        actions = []
        
        for i, finding in enumerate(top_findings, 1):
            severity = finding.get("severity", "medium").title()
            recommendation = finding.get("recommendation", "Review and remediate this issue")
            
            action = {
                "priority": i,
                "severity": severity,
                "action": recommendation,
                "urgency": "Immediate" if severity.lower() == "critical" else 
                         "High" if severity.lower() == "high" else
                         "Medium" if severity.lower() == "medium" else "Low",
                "finding_type": finding.get("type", "Security Issue")
            }
            actions.append(action)
        
        return actions
    
    def _prepare_report_data(self, session_data: Dict[str, Any], ai_summary: str = None) -> Dict[str, Any]:
        """Prepare data for report generation"""
        results = session_data.get("results", {})
        
        # Aggregate statistics
        total_tools = len(results)
        successful_tools = sum(1 for r in results.values() if r.get("success", False))
        failed_tools = total_tools - successful_tools
        
        # Aggregate findings
        all_findings = []
        findings_by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for tool_name, tool_result in results.items():
            analysis = tool_result.get("analysis", {})
            if analysis and "findings" in analysis:
                for finding in analysis["findings"]:
                    finding["tool"] = tool_name
                    all_findings.append(finding)
                    
                    severity = finding.get("severity", "low").lower()
                    if severity in findings_by_severity:
                        findings_by_severity[severity] += 1
        
        # Sort findings by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        all_findings.sort(key=lambda x: severity_order.get(x.get("severity", "low").lower(), 3))
        
        return {
            "session_id": session_data.get("session_id", "Unknown"),
            "timestamp": session_data.get("timestamp", datetime.now().isoformat()),
            "criteria": session_data.get("criteria", "No criteria specified"),
            "ai_summary": ai_summary or "No AI summary available",
            "statistics": {
                "total_tools": total_tools,
                "successful_tools": successful_tools,
                "failed_tools": failed_tools,
                "total_findings": len(all_findings),
                "findings_by_severity": findings_by_severity
            },
            "findings": all_findings,
            "tool_results": results,
            "generation_time": datetime.now().isoformat()
        }
    
    def _generate_enhanced_html_report(self, report_data: Dict[str, Any], session_id: str, timestamp: str) -> Optional[str]:
        """Generate enhanced user-friendly HTML report"""
        try:
            template = Template(self._get_enhanced_html_template())
            html_content = template.render(**report_data)
            
            filename = f"{session_id}_comprehensive_report_{timestamp}.html"
            file_path = self.reports_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logging.info(f"Enhanced HTML report generated: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logging.error(f"Failed to generate enhanced HTML report: {e}")
            return None
    
    def _generate_enhanced_markdown_report(self, report_data: Dict[str, Any], session_id: str, timestamp: str) -> Optional[str]:
        """Generate enhanced user-friendly Markdown report"""
        try:
            template = Template(self._get_enhanced_markdown_template())
            markdown_content = template.render(**report_data)
            
            filename = f"{session_id}_comprehensive_report_{timestamp}.md"
            file_path = self.reports_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logging.info(f"Enhanced Markdown report generated: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logging.error(f"Failed to generate enhanced Markdown report: {e}")
            return None
    
    def _generate_pdf_report(self, report_data: Dict[str, Any], session_id: str, timestamp: str) -> Optional[str]:
        """Generate PDF report using ReportLab"""
        if not REPORTLAB_AVAILABLE:
            logging.warning("ReportLab not available, skipping PDF generation")
            return None
        
        try:
            filename = f"{session_id}_report_{timestamp}.pdf"
            file_path = self.reports_dir / filename
            
            doc = SimpleDocTemplate(str(file_path), pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.darkblue,
                alignment=1  # Center
            )
            story.append(Paragraph("AutoPentest AI Report", title_style))
            story.append(Spacer(1, 12))
            
            # Session Info
            story.append(Paragraph(f"<b>Session ID:</b> {report_data['session_id']}", styles['Normal']))
            story.append(Paragraph(f"<b>Generated:</b> {report_data['generation_time'][:19]}", styles['Normal']))
            story.append(Paragraph(f"<b>Criteria:</b> {report_data['criteria']}", styles['Normal']))
            story.append(Spacer(1, 12))
            
            # AI Summary
            story.append(Paragraph("Executive Summary", styles['Heading2']))
            story.append(Paragraph(report_data['ai_summary'], styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Statistics
            stats = report_data['statistics']
            story.append(Paragraph("Test Statistics", styles['Heading2']))
            
            stats_data = [
                ['Metric', 'Value'],
                ['Total Tools Run', str(stats['total_tools'])],
                ['Successful Tools', str(stats['successful_tools'])],
                ['Failed Tools', str(stats['failed_tools'])],
                ['Total Findings', str(stats['total_findings'])],
                ['Critical Findings', str(stats['findings_by_severity']['critical'])],
                ['High Severity', str(stats['findings_by_severity']['high'])],
                ['Medium Severity', str(stats['findings_by_severity']['medium'])],
                ['Low Severity', str(stats['findings_by_severity']['low'])]
            ]
            
            stats_table = Table(stats_data)
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(stats_table)
            story.append(Spacer(1, 12))
            
            # Findings
            if report_data['findings']:
                story.append(Paragraph("Security Findings", styles['Heading2']))
                
                for i, finding in enumerate(report_data['findings'][:10]):  # Limit to top 10
                    severity = finding.get('severity', 'unknown').upper()
                    story.append(Paragraph(f"<b>Finding #{i+1} - {severity}</b>", styles['Heading3']))
                    story.append(Paragraph(f"<b>Tool:</b> {finding.get('tool', 'Unknown')}", styles['Normal']))
                    story.append(Paragraph(f"<b>Type:</b> {finding.get('type', 'Unknown')}", styles['Normal']))
                    story.append(Paragraph(f"<b>Details:</b> {finding.get('details', 'No details')}", styles['Normal']))
                    story.append(Paragraph(f"<b>Recommendation:</b> {finding.get('recommendation', 'No recommendation')}", styles['Normal']))
                    story.append(Spacer(1, 8))
            
            doc.build(story)
            logging.info(f"PDF report generated: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logging.error(f"Failed to generate PDF report: {e}")
            return None
    
    def _generate_json_report(self, report_data: Dict[str, Any], session_id: str, timestamp: str) -> Optional[str]:
        """Generate JSON report"""
        try:
            filename = f"{session_id}_report_{timestamp}.json"
            file_path = self.reports_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            logging.info(f"JSON report generated: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logging.error(f"Failed to generate JSON report: {e}")
            return None
    
    def list_reports(self) -> List[Dict[str, str]]:
        """List all generated reports"""
        reports = []
        
        try:
            for report_file in self.reports_dir.glob("*_report_*"):
                stat = report_file.stat()
                reports.append({
                    "name": report_file.name,
                    "path": str(report_file),
                    "date": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "size": self._format_file_size(stat.st_size)
                })
        except Exception as e:
            logging.error(f"Error listing reports: {e}")
        
        return sorted(reports, key=lambda x: x["date"], reverse=True)
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def _get_enhanced_html_template(self) -> str:
        """Get enhanced user-friendly HTML report template"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AegisSec Security Assessment Report - {{ session_id }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background-color: #f8f9fa; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 15px; margin-bottom: 30px; text-align: center; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header .subtitle { font-size: 1.2em; opacity: 0.9; margin-bottom: 5px; }
        .header .developed-by { font-size: 0.9em; opacity: 0.8; }
        
        .summary-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
        .card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 5px solid #667eea; }
        .card.score { border-left-color: {{ security_score.color }}; }
        .card.critical { border-left-color: #dc3545; }
        .card.high { border-left-color: #fd7e14; }
        .card.medium { border-left-color: #ffc107; }
        .card.good { border-left-color: #28a745; }
        
        .card-title { font-size: 1.1em; font-weight: 600; color: #495057; margin-bottom: 10px; }
        .card-value { font-size: 2.2em; font-weight: bold; margin-bottom: 5px; }
        .card-description { font-size: 0.9em; color: #6c757d; }
        
        .section { background: white; margin: 30px 0; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .section-title { font-size: 1.5em; font-weight: 600; color: #495057; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #e9ecef; }
        
        .executive-summary { background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%); border-left: 5px solid #28a745; padding: 25px; border-radius: 8px; margin: 20px 0; }
        .executive-summary h3 { color: #155724; margin-bottom: 15px; }
        .executive-summary p { color: #155724; line-height: 1.7; }
        
        .priority-actions { margin: 20px 0; }
        .action-item { background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 15px; margin: 10px 0; }
        .action-item.immediate { background: #f8d7da; border-color: #f5c6cb; }
        .action-item.high { background: #fff3cd; border-color: #ffeaa7; }
        .action-item.medium { background: #d1ecf1; border-color: #bee5eb; }
        .action-urgent { font-weight: bold; color: #721c24; }
        .action-high { font-weight: bold; color: #856404; }
        .action-medium { font-weight: bold; color: #0c5460; }
        
        .findings-grid { display: grid; gap: 15px; margin: 20px 0; }
        .finding-item { background: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; }
        .finding-item.critical { border-left: 5px solid #dc3545; background: #fdf2f2; }
        .finding-item.high { border-left: 5px solid #fd7e14; background: #fef9f3; }
        .finding-item.medium { border-left: 5px solid #ffc107; background: #fffbf0; }
        .finding-item.low { border-left: 5px solid #28a745; background: #f8fff8; }
        
        .finding-header { display: flex; justify-content: between; align-items: center; margin-bottom: 10px; }
        .finding-severity { padding: 4px 12px; border-radius: 20px; font-size: 0.8em; font-weight: bold; text-transform: uppercase; }
        .severity-critical { background: #dc3545; color: white; }
        .severity-high { background: #fd7e14; color: white; }
        .severity-medium { background: #ffc107; color: black; }
        .severity-low { background: #28a745; color: white; }
        
        .tool-results-grid { display: grid; gap: 15px; margin: 20px 0; }
        .tool-result { background: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; }
        .tool-result.success { border-left: 5px solid #28a745; }
        .tool-result.failure { border-left: 5px solid #dc3545; }
        
        .command-box { background: #2d3748; color: #e2e8f0; padding: 15px; border-radius: 5px; font-family: 'Courier New', monospace; font-size: 0.9em; overflow-x: auto; margin: 10px 0; }
        
        .intelligence-badge { display: inline-block; background: #667eea; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.7em; margin-left: 10px; }
        
        .footer { text-align: center; margin-top: 50px; padding: 30px; background: #f8f9fa; border-radius: 10px; }
        .footer p { color: #6c757d; margin: 5px 0; }
        
        @media (max-width: 768px) {
            .container { padding: 10px; }
            .header { padding: 20px; }
            .header h1 { font-size: 2em; }
            .summary-cards { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ AegisSec Security Assessment</h1>
            <div class="subtitle">Comprehensive Penetration Testing Report</div>
            <div class="developed-by">Powered by AI • Developed by RunTime Terrors</div>
            <div style="margin-top: 15px; font-size: 0.9em;">
                <strong>Session:</strong> {{ session_id }} | 
                <strong>Generated:</strong> {{ generation_time[:19] }}
            </div>
        </div>

        <!-- Security Score Overview -->
        <div class="summary-cards">
            <div class="card score" style="border-left-color: {{ security_score.color }};">
                <div class="card-title">🔒 Security Score</div>
                <div class="card-value" style="color: {{ security_score.color }};">{{ security_score.score }}%</div>
                <div class="card-description">{{ security_score.rating }} - {{ security_score.description }}</div>
            </div>
            <div class="card">
                <div class="card-title">🔍 Tools Executed</div>
                <div class="card-value">{{ statistics.successful_tools }}/{{ statistics.total_tools }}</div>
                <div class="card-description">{{ statistics.success_rate }}% Success Rate</div>
            </div>
            <div class="card">
                <div class="card-title">⚠️ Issues Found</div>
                <div class="card-value">{{ statistics.total_findings }}</div>
                <div class="card-description">
                    {{ statistics.findings_by_severity.critical }} Critical, 
                    {{ statistics.findings_by_severity.high }} High Priority
                </div>
            </div>
            <div class="card">
                <div class="card-title">🤖 AI Intelligence</div>
                <div class="card-value">{{ statistics.intelligence_metrics.ai_interactions }}</div>
                <div class="card-description">
                    {% if statistics.intelligence_metrics.intelligent_execution %}
                    Smart Execution Enabled
                    {% else %}
                    Standard Execution
                    {% endif %}
                </div>
            </div>
        </div>

        <!-- Executive Summary -->
        <div class="section">
            <h2 class="section-title">📊 Executive Summary</h2>
            <div class="executive-summary">
                <h3>Security Assessment Overview</h3>
                <p>{{ executive_summary }}</p>
            </div>
        </div>

        <!-- Priority Actions -->
        {% if priority_actions %}
        <div class="section">
            <h2 class="section-title">🎯 Priority Actions Required</h2>
            <div class="priority-actions">
                {% for action in priority_actions %}
                <div class="action-item {{ action.urgency.lower() }}">
                    <div class="action-{{ action.urgency.lower() }}">
                        #{{ action.priority }} - {{ action.urgency }} Priority
                    </div>
                    <strong>{{ action.finding_type }}:</strong> {{ action.action }}
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        <!-- Key Findings -->
        {% if priority_findings %}
        <div class="section">
            <h2 class="section-title">🔍 Key Security Findings</h2>
            <div class="findings-grid">
                {% for finding in priority_findings %}
                <div class="finding-item {{ finding.severity.lower() }}">
                    <div class="finding-header">
                        <h4>{{ finding.readable_description }}</h4>
                        <span class="finding-severity severity-{{ finding.severity.lower() }}">
                            {{ finding.severity }}
                        </span>
                    </div>
                    <p><strong>Discovered by:</strong> {{ finding.tool }}</p>
                    <p><strong>Technical Details:</strong> {{ finding.details }}</p>
                    <p><strong>Recommendation:</strong> {{ finding.recommendation }}</p>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        <!-- Tool Execution Results -->
        <div class="section">
            <h2 class="section-title">🛠️ Tool Execution Summary</h2>
            <div class="tool-results-grid">
                {% for tool_name, result in tool_results.items() %}
                <div class="tool-result {% if result.success %}success{% else %}failure{% endif %}">
                    <h4>
                        {{ tool_name }}
                        {% if result.get('ai_enhanced', False) %}
                        <span class="intelligence-badge">AI Enhanced</span>
                        {% endif %}
                    </h4>
                    <div class="command-box">{{ result.command }}</div>
                    <p><strong>Status:</strong> 
                        {% if result.success %}
                        <span style="color: #28a745;">✅ Completed Successfully</span>
                        {% else %}
                        <span style="color: #dc3545;">❌ Failed</span>
                        {% endif %}
                    </p>
                    <p><strong>Execution Time:</strong> {{ "%.2f"|format(result.execution_time) }} seconds</p>
                    {% if result.analysis and result.analysis.findings %}
                    <p><strong>Findings:</strong> {{ result.analysis.findings|length }} issues discovered</p>
                    {% endif %}
                    {% if result.error %}
                    <p><strong>Error:</strong> <span style="color: #dc3545;">{{ result.error }}</span></p>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p><strong>🛡️ AegisSec Security Assessment Report</strong></p>
            <p>Developed by RunTime Terrors • Powered by DeepSeek AI</p>
            <p>Generated on {{ generation_time[:19] }} • Report Version {{ report_metadata.report_version }}</p>
            <p style="font-size: 0.8em; margin-top: 15px; color: #999;">
                This report contains sensitive security information. Please handle with appropriate care and share only with authorized personnel.
            </p>
        </div>
    </div>
</body>
</html>
        """
    
    def _get_markdown_template(self) -> str:
        """Get Markdown report template"""
        return """# 🤖 AutoPentest AI Report

**Session ID:** {{ session_id }}  
**Generated:** {{ generation_time[:19] }}  
**Test Criteria:** {{ criteria }}

## 📊 Executive Summary

{{ ai_summary }}

## 📈 Test Statistics

| Metric | Value |
|--------|-------|
| Tools Run | {{ statistics.total_tools }} |
| Successful | {{ statistics.successful_tools }} |
| Failed | {{ statistics.failed_tools }} |
| Total Findings | {{ statistics.total_findings }} |
| Critical | {{ statistics.findings_by_severity.critical }} |
| High | {{ statistics.findings_by_severity.high }} |
| Medium | {{ statistics.findings_by_severity.medium }} |
| Low | {{ statistics.findings_by_severity.low }} |

{% if findings %}
## 🔍 Security Findings

{% for finding in findings %}
### {{ finding.type|title }} ({{ finding.severity|upper }})

**Tool:** {{ finding.tool }}  
**Details:** {{ finding.details }}  
**Recommendation:** {{ finding.recommendation }}

---
{% endfor %}
{% endif %}

## 🛠️ Tool Execution Results

{% for tool_name, result in tool_results.items() %}
### {{ tool_name }}

**Command:** `{{ result.command }}`  
**Status:** {% if result.success %}✅ Success{% else %}❌ Failed{% endif %}  
**Execution Time:** {{ "%.2f"|format(result.execution_time) }}s  
{% if result.error %}**Error:** {{ result.error }}{% endif %}

---
{% endfor %}

*Generated by AegisSec | {{ generation_time[:19] }}*
"""
    
    def _get_enhanced_markdown_template(self) -> str:
        """Get Enhanced Markdown report template"""
        return """# 🛡️ AegisSec Security Assessment Report

**Session ID:** {{ session_id }}  
**Generated:** {{ generation_time[:19] }}  
**Test Criteria:** {{ criteria }}

## 📊 Executive Summary

{{ ai_summary }}

## 📈 Test Statistics

| Metric | Value |
|--------|-------|
| Tools Run | {{ statistics.total_tools }} |
| Successful | {{ statistics.successful_tools }} |
| Failed | {{ statistics.failed_tools }} |
| Total Findings | {{ statistics.total_findings }} |
| AI Interactions | {{ statistics.intelligence_metrics.ai_interactions }} |
| Adaptive Commands | {{ statistics.intelligence_metrics.adaptive_commands }} |

{% if findings %}
## 🔍 Security Findings

{% for finding in findings %}
### {{ finding.type|title }} ({{ finding.severity|upper }})

**Tool:** {{ finding.tool }}  
**Details:** {{ finding.details }}  
**Recommendation:** {{ finding.recommendation }}

---
{% endfor %}
{% endif %}

## 🛠️ Tool Execution Results

{% for tool_name, result in tool_results.items() %}
### {{ tool_name }}

**Command:** `{{ result.command }}`  
**Status:** {% if result.success %}✅ Success{% else %}❌ Failed{% endif %}  
**Execution Time:** {{ "%.2f"|format(result.get('duration', 0)) }}s  
{% if result.error %}**Error:** {{ result.error }}{% endif %}

---
{% endfor %}

*Generated by AegisSec - Runtime Terrors Team | {{ generation_time[:19] }}*
"""
    
    def _get_html_template(self) -> str:
        """Get HTML report template"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AegisSec Security Report - {{ session_id }}</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            line-height: 1.6; 
            margin: 0; 
            padding: 40px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            padding: 40px; 
            border-radius: 15px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            border-radius: 10px;
        }
        h1 { 
            color: white; 
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
            margin-top: 10px;
        }
        h2 { 
            color: #2c3e50; 
            margin-top: 40px; 
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }
        h3 { color: #34495e; }
        .meta { 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 8px; 
            margin: 20px 0;
            border-left: 4px solid #3498db;
        }
        .summary { 
            background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%); 
            padding: 25px; 
            border-radius: 8px; 
            border-left: 5px solid #27ae60;
            margin: 20px 0;
        }
        .security-score {
            text-align: center;
            padding: 30px;
            margin: 20px 0;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 10px;
        }
        .score-circle {
            display: inline-block;
            width: 120px;
            height: 120px;
            border-radius: 50%;
            line-height: 120px;
            font-size: 2em;
            font-weight: bold;
            color: white;
            margin: 10px;
        }
        .score-good { background: linear-gradient(135deg, #27ae60, #2ecc71); }
        .score-medium { background: linear-gradient(135deg, #f39c12, #e67e22); }
        .score-poor { background: linear-gradient(135deg, #e74c3c, #c0392b); }
        .stats-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin: 30px 0; 
        }
        .stat-card { 
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
            padding: 25px; 
            border-radius: 10px; 
            text-align: center; 
            border: 1px solid #dee2e6;
            transition: transform 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        .stat-value { 
            font-size: 2.5em; 
            font-weight: bold; 
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .stat-label { 
            color: #6c757d; 
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .finding { 
            background: white; 
            border: 1px solid #ddd; 
            border-radius: 8px; 
            padding: 20px; 
            margin: 15px 0;
            transition: box-shadow 0.3s ease;
        }
        .finding:hover {
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .severity-critical { border-left: 5px solid #dc3545; background: #fff5f5; }
        .severity-high { border-left: 5px solid #fd7e14; background: #fff8f0; }
        .severity-medium { border-left: 5px solid #ffc107; background: #fffbf0; }
        .severity-low { border-left: 5px solid #28a745; background: #f8fff8; }
        .tool-results { margin-top: 40px; }
        .tool-result { 
            background: #f8f9fa; 
            border-radius: 8px; 
            padding: 20px; 
            margin: 15px 0;
            border-left: 4px solid #6c757d;
        }
        .success { border-left-color: #28a745; }
        .failure { border-left-color: #dc3545; }
        .command { 
            background: #2d3748; 
            color: #e2e8f0; 
            padding: 15px; 
            border-radius: 5px; 
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace; 
            overflow-x: auto;
            margin: 10px 0;
        }
        .footer {
            margin-top: 50px;
            padding: 30px;
            text-align: center;
            background: #f8f9fa;
            border-radius: 10px;
            color: #6c757d;
        }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }
        .badge-critical { background: #dc3545; color: white; }
        .badge-high { background: #fd7e14; color: white; }
        .badge-medium { background: #ffc107; color: #212529; }
        .badge-low { background: #28a745; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ AegisSec Security Report</h1>
            <div class="subtitle">AI-Powered Penetration Testing Analysis</div>
            <div class="subtitle">Developed by RunTime Terrors</div>
        </div>
        
        <div class="meta">
            <strong>📋 Session ID:</strong> {{ session_id }}<br>
            <strong>📅 Generated:</strong> {{ generation_time[:19] }}<br>
            <strong>🎯 Test Criteria:</strong> {{ criteria }}
        </div>
        
        <div class="security-score">
            <h2>🏆 Security Assessment Score</h2>
            {% set score = 100 - (statistics.findings_by_severity.critical * 20) - (statistics.findings_by_severity.high * 10) %}
            {% if score >= 70 %}
                <div class="score-circle score-good">{{ score }}%</div>
                <p><strong>Status:</strong> <span style="color: #27ae60;">Good Security Posture</span></p>
            {% elif score >= 40 %}
                <div class="score-circle score-medium">{{ score }}%</div>
                <p><strong>Status:</strong> <span style="color: #f39c12;">Needs Improvement</span></p>
            {% else %}
                <div class="score-circle score-poor">{{ score }}%</div>
                <p><strong>Status:</strong> <span style="color: #e74c3c;">Critical Issues Found</span></p>
            {% endif %}
        </div>
        
        <h2>📊 Executive Summary</h2>
        <div class="summary">
            {{ ai_summary | replace('\n', '<br>') | safe }}
        </div>
        
        <h2>📈 Assessment Statistics</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{{ statistics.total_tools }}</div>
                <div class="stat-label">Tools Executed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ statistics.successful_tools }}</div>
                <div class="stat-label">Successful Scans</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ statistics.total_findings }}</div>
                <div class="stat-label">Total Findings</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ statistics.findings_by_severity.critical }}</div>
                <div class="stat-label">Critical Issues</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ statistics.findings_by_severity.high }}</div>
                <div class="stat-label">High Priority</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ statistics.findings_by_severity.medium }}</div>
                <div class="stat-label">Medium Risk</div>
            </div>
        </div>
        
        {% if findings %}
        <h2>🔍 Security Findings</h2>
        {% for finding in findings %}
        <div class="finding severity-{{ finding.severity|lower }}">
            <h3>
                {{ finding.type|title }} 
                <span class="badge badge-{{ finding.severity|lower }}">{{ finding.severity|upper }}</span>
            </h3>
            <p><strong>🛠️ Detected by:</strong> {{ finding.tool }}</p>
            <p><strong>📝 Details:</strong> {{ finding.details }}</p>
            <p><strong>💡 Recommendation:</strong> {{ finding.recommendation }}</p>
        </div>
        {% endfor %}
        {% endif %}
        
        <h2>🛠️ Tool Execution Details</h2>
        <div class="tool-results">
            {% for tool_name, result in tool_results.items() %}
            <div class="tool-result {% if result.success %}success{% else %}failure{% endif %}">
                <h3>{{ tool_name }} {% if result.success %}✅{% else %}❌{% endif %}</h3>
                <div class="command">{{ result.command }}</div>
                <p><strong>⏱️ Execution Time:</strong> {{ "%.2f"|format(result.execution_time) }} seconds</p>
                <p><strong>📊 Status:</strong> {% if result.success %}Successfully completed{% else %}Failed to execute{% endif %}</p>
                {% if result.error %}
                <p><strong>⚠️ Error:</strong> {{ result.error }}</p>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        
        <div class="footer">
            <p><strong>🛡️ Generated by AegisSec</strong></p>
            <p>AI-Powered Penetration Testing Platform</p>
            <p>Developed by RunTime Terrors | {{ generation_time[:19] }}</p>
            <p><em>This report is for authorized security testing purposes only</em></p>
        </div>
    </div>
</body>
</html>
        """
