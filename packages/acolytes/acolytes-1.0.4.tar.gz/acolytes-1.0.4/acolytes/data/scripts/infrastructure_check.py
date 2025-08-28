#!/usr/bin/env python3
"""
Infrastructure Detection Script for Acolytes for Claude Code Setup
Analyzes project infrastructure, deployment, databases, CI/CD, and external services
"""

import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

class InfrastructureChecker:
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.results: Dict[str, Any] = {
            "project_path": str(self.project_path),
            "containerization": {},
            "orchestration": {},
            "databases": {},
            "cicd": {},
            "cloud_iac": {},
            "external_services": {},
            "security": {},
            "networking": {},
            "monitoring": {},
            "errors": []
        }
        # Ensure errors is a list for type safety
        if not isinstance(self.results["errors"], list):
            self.results["errors"] = []
        
    def run_command(self, command: str, shell: bool = True) -> Optional[str]:
        """Execute command and return output"""
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=5,
                cwd=self.project_path
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except subprocess.TimeoutExpired:
            self.results["errors"].append(f"Command timed out: {command[:50]}...")
            return None
        except subprocess.SubprocessError as e:
            self.results["errors"].append(f"Command error: {type(e).__name__}")
            return None
        except Exception as e:
            self.results["errors"].append(f"Unexpected error: {type(e).__name__}")
            return None
    
    def file_exists(self, path: str) -> bool:
        """Check if file exists relative to project"""
        try:
            # Validate path to prevent traversal attacks
            file_path = (self.project_path / path).resolve()
            # Ensure the resolved path is within project directory
            if not str(file_path).startswith(str(self.project_path)):
                return False
            return file_path.exists()
        except (ValueError, OSError):
            return False
    
    def find_files(self, pattern: str, max_results: int = 10) -> List[str]:
        """Find files matching pattern"""
        try:
            files = []
            for match in self.project_path.rglob(pattern):
                if match.is_file():
                    relative_path = str(match.relative_to(self.project_path))
                    # Skip .claude/memory and .claude/chat files
                    if (relative_path.startswith('.claude\\memory\\') or 
                        relative_path.startswith('.claude\\chat\\') or
                        relative_path.startswith('.claude/memory/') or 
                        relative_path.startswith('.claude/chat/') or
                        'session_' in relative_path):
                        continue
                    files.append(relative_path)
                    if len(files) >= max_results:
                        break
            return files
        except Exception as e:
            self.results["errors"].append(f"Find files failed: {pattern} - {str(e)}")
            return []
    
    def read_file_lines(self, path: str, max_lines: int = 50) -> List[str]:
        """Read first N lines of a file"""
        try:
            file_path = (self.project_path / path).resolve()
            # Validate path to prevent traversal attacks
            if not str(file_path).startswith(str(self.project_path)):
                return []
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = []
                    for _ in range(max_lines):
                        line = f.readline()
                        if not line:  # EOF reached
                            break
                        lines.append(line.strip())
                    return lines
            return []
        except Exception as e:
            self.results["errors"].append(f"Read file failed: {path} - {str(e)}")
            return []
    
    def detect_in_file(self, path: str, patterns: List[str]) -> Dict[str, bool]:
        """Detect patterns in file"""
        results = {pattern: False for pattern in patterns}
        try:
            file_path = (self.project_path / path).resolve()
            # Validate path to prevent traversal attacks
            if not str(file_path).startswith(str(self.project_path)):
                return results
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for pattern in patterns:
                        if pattern.lower() in content.lower():
                            results[pattern] = True
        except Exception:
            pass
        return results
    
    def check_containerization(self):
        """Check Docker and container configuration"""
        docker = {
            "enabled": False,
            "dockerfiles": [],
            "compose_files": [],
            "services": [],
            "images": []
        }
        
        # Check Dockerfiles
        docker["dockerfiles"] = self.find_files("Dockerfile*")
        if docker["dockerfiles"]:
            docker["enabled"] = True
            
        # Check docker-compose files
        compose_files = self.find_files("docker-compose*.yml") + self.find_files("docker-compose*.yaml")
        docker["compose_files"] = compose_files
        
        # Parse docker-compose for services
        if compose_files and compose_files[0]:
            try:
                import yaml
                with open(self.project_path / compose_files[0], 'r') as f:
                    compose_data = yaml.safe_load(f)
                    if compose_data and 'services' in compose_data:
                        docker["services"] = list(compose_data['services'].keys())
            except (ImportError, FileNotFoundError, Exception):
                # If yaml parsing fails, try basic parsing
                lines = self.read_file_lines(compose_files[0])
                in_services = False
                for line in lines:
                    stripped = line.strip()
                    if stripped == 'services:':
                        in_services = True
                        continue
                    if in_services and stripped and not stripped.startswith('#'):
                        if ':' in stripped and not stripped.startswith(' '):
                            # This is a service definition
                            service = stripped.split(':')[0].strip()
                            if service not in ['version', 'networks', 'volumes']:
                                docker["services"].append(service)
                        elif not stripped.startswith(' ') and stripped.endswith(':'):
                            # End of services section
                            break
        
        self.results["containerization"]["docker"] = docker
        
        # Check for other container tools
        self.results["containerization"]["podman"] = self.file_exists("Containerfile")
        self.results["containerization"]["buildah"] = self.file_exists(".buildah")
        
    def check_orchestration(self):
        """Check Kubernetes and orchestration"""
        k8s = {
            "enabled": False,
            "manifests": [],
            "helm_charts": [],
            "kustomize": False
        }
        
        # Check for Kubernetes manifests
        k8s["manifests"] = self.find_files("*.yaml", 20)
        k8s["manifests"] = [f for f in k8s["manifests"] if any(
            kw in f.lower() for kw in ['k8s', 'kubernetes', 'deployment', 'service', 'ingress']
        )]
        
        if k8s["manifests"]:
            k8s["enabled"] = True
            
        # Check for Helm
        if self.file_exists("Chart.yaml") or self.find_files("**/Chart.yaml"):
            k8s["helm_charts"] = self.find_files("**/Chart.yaml")
            
        # Check for Kustomize
        k8s["kustomize"] = bool(self.find_files("kustomization.yaml"))
        
        self.results["orchestration"]["kubernetes"] = k8s
        
        # Check for other orchestration tools
        self.results["orchestration"]["swarm"] = bool(self.find_files("docker-stack.yml"))
        self.results["orchestration"]["nomad"] = bool(self.find_files("*.nomad"))
        
    def check_databases(self):
        """Check database configuration and migrations"""
        db = {
            "migrations": [],
            "sql_files": [],
            "detected_types": [],
            "migration_tools": []
        }
        
        # Find migration directories
        migration_dirs = ['migrations', 'db/migrations', 'database/migrations', 'prisma/migrations']
        for dir_name in migration_dirs:
            if self.file_exists(dir_name):
                db["migrations"].append(dir_name)
                
        # Find SQL files
        db["sql_files"] = self.find_files("*.sql", 20)
        
        # Detect database types from config files
        config_files = ['package.json', 'composer.json', 'requirements.txt', 'Gemfile', 'go.mod']
        db_keywords = {
            'postgresql': ['postgres', 'pg', 'psql'],
            'mysql': ['mysql', 'mariadb'],
            'mongodb': ['mongodb', 'mongoose'],
            'redis': ['redis', 'ioredis'],
            'sqlite': ['sqlite', 'sqlite3'],
            'elasticsearch': ['elasticsearch', 'elastic']
        }
        
        for config_file in config_files:
            if self.file_exists(config_file):
                detections = self.detect_in_file(config_file, sum(db_keywords.values(), []))
                for db_type, keywords in db_keywords.items():
                    if any(detections.get(kw, False) for kw in keywords):
                        db["detected_types"].append(db_type)
                        
        # Detect migration tools
        tool_indicators = {
            'laravel': 'database/migrations',
            'django': 'migrations/__init__.py',
            'rails': 'db/migrate',
            'flyway': 'flyway.conf',
            'liquibase': 'liquibase.properties',
            'prisma': 'prisma/schema.prisma',
            'typeorm': 'ormconfig.json',
            'sequelize': '.sequelizerc'
        }
        
        for tool, indicator in tool_indicators.items():
            if self.file_exists(indicator):
                db["migration_tools"].append(tool)
                
        self.results["databases"] = db
        
    def check_cicd(self):
        """Check CI/CD configuration"""
        cicd = {
            "platform": "none",
            "workflows": [],
            "config_files": []
        }
        
        # Check GitHub Actions
        if self.file_exists(".github/workflows"):
            cicd["platform"] = "github-actions"
            cicd["workflows"] = self.find_files(".github/workflows/*.yml") + self.find_files(".github/workflows/*.yaml")
            cicd["config_files"] = cicd["workflows"]
            
        # Check GitLab CI
        elif self.file_exists(".gitlab-ci.yml"):
            cicd["platform"] = "gitlab-ci"
            cicd["config_files"] = [".gitlab-ci.yml"]
            
        # Check Jenkins
        elif self.file_exists("Jenkinsfile"):
            cicd["platform"] = "jenkins"
            cicd["config_files"] = ["Jenkinsfile"]
            
        # Check CircleCI
        elif self.file_exists(".circleci/config.yml"):
            cicd["platform"] = "circleci"
            cicd["config_files"] = [".circleci/config.yml"]
            
        # Check Travis CI
        elif self.file_exists(".travis.yml"):
            cicd["platform"] = "travis"
            cicd["config_files"] = [".travis.yml"]
            
        # Check Azure DevOps
        elif self.file_exists("azure-pipelines.yml"):
            cicd["platform"] = "azure-devops"
            cicd["config_files"] = ["azure-pipelines.yml"]
            
        self.results["cicd"] = cicd
        
    def check_cloud_iac(self):
        """Check Infrastructure as Code and cloud configuration"""
        iac = {
            "terraform": {
                "enabled": False,
                "files": []
            },
            "cloudformation": {
                "enabled": False,
                "files": []
            },
            "pulumi": {
                "enabled": False,
                "files": []
            },
            "serverless": {
                "enabled": False,
                "files": []
            },
            "detected_providers": []
        }
        
        # Check Terraform
        tf_files = self.find_files("*.tf")
        if tf_files:
            iac["terraform"]["enabled"] = True
            iac["terraform"]["files"] = tf_files
            
        # Check CloudFormation
        cf_files = self.find_files("*cloudformation*.yaml") + self.find_files("*cloudformation*.json")
        cf_files += self.find_files("*cfn*.yaml") + self.find_files("*cfn*.json")
        if cf_files:
            iac["cloudformation"]["enabled"] = True
            iac["cloudformation"]["files"] = cf_files
            
        # Check Pulumi
        if self.file_exists("Pulumi.yaml"):
            iac["pulumi"]["enabled"] = True
            iac["pulumi"]["files"] = ["Pulumi.yaml"]
            
        # Check Serverless Framework
        serverless_files = self.find_files("serverless.yml") + self.find_files("serverless.yaml")
        if serverless_files:
            iac["serverless"]["enabled"] = True
            iac["serverless"]["files"] = serverless_files
            
        # Detect cloud providers
        provider_indicators = {
            'aws': ['.aws', 'aws.config', 'sam-template'],
            'gcp': ['.gcloud', 'app.yaml', 'gcp.config'],
            'azure': ['.azure', 'azure.config', 'azure-pipelines.yml'],
            'vercel': ['vercel.json', '.vercel'],
            'netlify': ['netlify.toml', '.netlify'],
            'heroku': ['Procfile', 'app.json']
        }
        
        for provider, indicators in provider_indicators.items():
            if any(self.file_exists(ind) for ind in indicators):
                iac["detected_providers"].append(provider)
                
        self.results["cloud_iac"] = iac
        
    def check_external_services(self):
        """Check external service integrations"""
        services = {
            "payment": [],
            "email": [],
            "authentication": [],
            "storage": [],
            "messaging": [],
            "analytics": []
        }
        
        # Files to check for service mentions (exclude chat/memory files)
        check_files = ['package.json', 'composer.json', 'requirements.txt', 'Gemfile', 'go.mod']
        check_files.extend(self.find_files("*.env.example")[:3])
        check_files.extend(self.find_files("*config*.js")[:3])
        config_json_files = self.find_files("*config*.json")[:3]
        
        # Filter out chat/memory files
        check_files.extend([f for f in config_json_files if f and 
                          not f.startswith('.claude/memory/') and 
                          not f.startswith('.claude/chat/') and
                          'session_' not in f])
        
        # Service patterns
        service_patterns = {
            "payment": ['stripe', 'paypal', 'square', 'braintree', 'razorpay'],
            "email": ['sendgrid', 'mailgun', 'ses', 'smtp', 'postmark', 'mailchimp'],
            "authentication": ['auth0', 'firebase-auth', 'cognito', 'okta', 'oauth'],
            "storage": ['s3', 'cloudinary', 'uploadcare', 'digitalocean-spaces'],
            "messaging": ['twilio', 'pusher', 'socket.io', 'rabbitmq', 'kafka'],
            "analytics": ['google-analytics', 'mixpanel', 'segment', 'amplitude']
        }
        
        for file_path in check_files:
            if self.file_exists(file_path):
                for service_type, patterns in service_patterns.items():
                    detections = self.detect_in_file(file_path, patterns)
                    for pattern, detected in detections.items():
                        if detected and pattern not in services[service_type]:
                            services[service_type].append(pattern)
                            
        self.results["external_services"] = services
        
    def check_security(self):
        """Check security configuration"""
        security = {
            "ssl_configured": False,
            "secrets_management": "unknown",
            "vulnerability_scanning": [],
            "security_files": []
        }
        
        # Check for SSL/TLS configuration
        ssl_indicators = ['cert.pem', 'key.pem', 'fullchain.pem', '.crt', '.key']
        security["ssl_configured"] = any(self.find_files(f"*{ind}") for ind in ssl_indicators)
        
        # Check secrets management
        if self.file_exists(".env.vault") or self.file_exists("vault.json"):
            security["secrets_management"] = "vault"
        elif self.file_exists(".env.example"):
            security["secrets_management"] = "env-files"
        elif self.find_files("**/secrets.yml"):
            security["secrets_management"] = "config-files"
            
        # Check vulnerability scanning
        vuln_tools = {
            'dependabot': '.github/dependabot.yml',
            'snyk': '.snyk',
            'trivy': '.trivyignore',
            'safety': '.safety-policy.json'
        }
        
        for tool, indicator in vuln_tools.items():
            if self.file_exists(indicator):
                security["vulnerability_scanning"].append(tool)
                
        # Security-related files
        sec_files = ['security.txt', '.security', 'SECURITY.md']
        security["security_files"] = [f for f in sec_files if self.file_exists(f)]
        
        self.results["security"] = security
        
    def check_monitoring(self):
        """Check monitoring and observability configuration"""
        monitoring = {
            "apm": [],
            "error_tracking": [],
            "logging": [],
            "metrics": []
        }
        
        # Check configuration files for monitoring services (exclude chat/memory files)
        config_files = []
        config_files.extend(self.find_files("*.config.js")[:5])
        config_files.extend(self.find_files("package.json"))
        config_files.extend(self.find_files("composer.json"))
        config_files.extend(self.find_files("requirements.txt"))
        config_files.extend(self.find_files("Gemfile"))
        config_files.extend(self.find_files("go.mod"))
        config_files.extend(self.find_files("*.env*")[:3])
        
        # Filter out chat/memory files
        check_files = [f for f in config_files if f and 
                      not f.startswith('.claude/memory/') and 
                      not f.startswith('.claude/chat/') and
                      'session_' not in f]
        
        monitoring_patterns = {
            "apm": ['newrelic', 'datadog', 'appdynamics', 'dynatrace'],
            "error_tracking": ['sentry', 'rollbar', 'bugsnag', 'airbrake'],
            "logging": ['winston', 'morgan', 'bunyan', 'pino', 'log4j', 'logback'],
            "metrics": ['prometheus', 'statsd', 'graphite', 'influxdb']
        }
        
        for file_path in check_files:
            if self.file_exists(file_path):
                for monitor_type, patterns in monitoring_patterns.items():
                    detections = self.detect_in_file(file_path, patterns)
                    for pattern, detected in detections.items():
                        if detected and pattern not in monitoring[monitor_type]:
                            monitoring[monitor_type].append(pattern)
                            
        self.results["monitoring"] = monitoring
        
    def check_networking(self):
        """Check networking and CDN configuration"""
        networking = {
            "load_balancer": "none",
            "cdn": "none",
            "reverse_proxy": "none",
            "api_gateway": "none"
        }
        
        # Check for load balancer configuration
        if self.file_exists("nginx.conf") or self.find_files("**/nginx.conf"):
            networking["reverse_proxy"] = "nginx"
        elif self.file_exists("haproxy.cfg"):
            networking["load_balancer"] = "haproxy"
            
        # Check for CDN
        cdn_indicators = {
            'cloudflare': ['cloudflare.json', '.cloudflare'],
            'cloudfront': ['cloudfront.config'],
            'fastly': ['fastly.toml']
        }
        
        for cdn, indicators in cdn_indicators.items():
            if any(self.file_exists(ind) for ind in indicators):
                networking["cdn"] = cdn
                
        # Check for API Gateway
        if self.find_files("kong.yml") or self.find_files("kong.conf"):
            networking["api_gateway"] = "kong"
        elif self.find_files("**/gateway.config.yml"):
            networking["api_gateway"] = "express-gateway"
            
        self.results["networking"] = networking
        
    def generate_summary(self):
        """Generate infrastructure summary"""
        summary = {
            "hosting_type": "unknown",
            "primary_database": "unknown",
            "deployment_method": "unknown",
            "containerized": False,
            "has_cicd": False,
            "external_dependencies_count": 0,
            "security_level": "unknown"
        }
        
        # Determine hosting type
        if self.results["cloud_iac"]["detected_providers"]:
            summary["hosting_type"] = self.results["cloud_iac"]["detected_providers"][0]
        elif self.results["containerization"]["docker"]["enabled"]:
            summary["hosting_type"] = "containerized"
            
        # Primary database
        if self.results["databases"]["detected_types"]:
            summary["primary_database"] = self.results["databases"]["detected_types"][0]
            
        # Deployment method
        if self.results["cicd"]["platform"] != "none":
            summary["deployment_method"] = "automated"
            summary["has_cicd"] = True
        else:
            summary["deployment_method"] = "manual"
            
        # Containerization
        summary["containerized"] = self.results["containerization"]["docker"]["enabled"]
        
        # Count external dependencies
        for service_type, services in self.results["external_services"].items():
            summary["external_dependencies_count"] += len(services)
            
        # Security level assessment
        vuln_scanning = len(self.results["security"]["vulnerability_scanning"]) > 0
        ssl = self.results["security"]["ssl_configured"]
        secrets = self.results["security"]["secrets_management"] != "unknown"
        
        if vuln_scanning and ssl and secrets:
            summary["security_level"] = "good"
        elif ssl and secrets:
            summary["security_level"] = "basic"
        else:
            summary["security_level"] = "needs-improvement"
            
        self.results["summary"] = summary
        
    def run(self):
        """Run all infrastructure checks"""
        print("Starting infrastructure analysis...")
        
        # Run all checks
        self.check_containerization()
        print("  - Containerization checked")
        
        self.check_orchestration()
        print("  - Orchestration checked")
        
        self.check_databases()
        print("  - Databases checked")
        
        self.check_cicd()
        print("  - CI/CD checked")
        
        self.check_cloud_iac()
        print("  - Cloud/IaC checked")
        
        self.check_external_services()
        print("  - External services checked")
        
        self.check_security()
        print("  - Security checked")
        
        self.check_monitoring()
        print("  - Monitoring checked")
        
        self.check_networking()
        print("  - Networking checked")
        
        self.generate_summary()
        print("  - Summary generated")
        
        return self.results
        
def main():
    """Main execution"""
    import sys
    
    # Determine project path
    project_path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    # Run infrastructure check
    checker = InfrastructureChecker(project_path)
    results = checker.run()
    
    # Output results as readable report
    print("\n" + "="*60)
    print("INFRASTRUCTURE ANALYSIS RESULTS")
    print("="*60)
    
    # Print summary
    summary = results.get("summary", {})
    print("\nSUMMARY:")
    print(f"  Hosting Type: {summary.get('hosting_type', 'unknown')}")
    print(f"  Primary Database: {summary.get('primary_database', 'unknown')}")
    print(f"  Deployment Method: {summary.get('deployment_method', 'unknown')}")
    print(f"  Containerized: {summary.get('containerized', False)}")
    print(f"  Has CI/CD: {summary.get('has_cicd', False)}")
    print(f"  External Dependencies: {summary.get('external_dependencies_count', 0)}")
    print(f"  Security Level: {summary.get('security_level', 'unknown')}")
    
    # Print containerization info
    docker = results.get("containerization", {}).get("docker", {})
    if docker.get("enabled"):
        print("\nCONTAINERIZATION:")
        print("  Docker Enabled: Yes")
        if docker.get("dockerfiles"):
            print(f"  Dockerfiles: {', '.join(docker['dockerfiles'])}")
        if docker.get("compose_files"):
            print(f"  Compose Files: {', '.join(docker['compose_files'])}")
        if docker.get("services"):
            print(f"  Services: {', '.join(docker['services'])}")
    
    # Print CI/CD info
    cicd = results.get("cicd", {})
    if cicd.get("platform") != "none":
        print("\nCI/CD:")
        print(f"  Platform: {cicd.get('platform')}")
        if cicd.get("workflows"):
            print(f"  Workflows: {len(cicd['workflows'])} found")
    
    # Print database info
    db = results.get("databases", {})
    if db.get("detected_types"):
        print("\nDATABASES:")
        print(f"  Types Detected: {', '.join(db['detected_types'])}")
        if db.get("migrations"):
            print(f"  Migration Dirs: {', '.join(db['migrations'])}")
        if db.get("migration_tools"):
            print(f"  Migration Tools: {', '.join(db['migration_tools'])}")
    
    # Print external services
    services = results.get("external_services", {})
    services_found = False
    for service_type, service_list in services.items():
        if service_list:
            if not services_found:
                print("\nEXTERNAL SERVICES:")
                services_found = True
            print(f"  {service_type.title()}: {', '.join(service_list)}")
    
    # Print cloud/IaC info
    iac = results.get("cloud_iac", {})
    if iac.get("detected_providers"):
        print("\nCLOUD PROVIDERS:")
        print(f"  Detected: {', '.join(iac['detected_providers'])}")
    
    if iac.get("terraform", {}).get("enabled"):
        print(f"  Terraform: {len(iac['terraform'].get('files', []))} files")
    if iac.get("serverless", {}).get("enabled"):
        print("  Serverless: Yes")
    
    # Print security info
    security = results.get("security", {})
    if security:
        print("\nSECURITY:")
        print(f"  SSL Configured: {security.get('ssl_configured', False)}")
        print(f"  Secrets Management: {security.get('secrets_management', 'unknown')}")
        if security.get("vulnerability_scanning"):
            print(f"  Vulnerability Scanning: {', '.join(security['vulnerability_scanning'])}")
    
    # Print monitoring info
    monitoring = results.get("monitoring", {})
    monitoring_found = False
    for monitor_type, monitor_list in monitoring.items():
        if monitor_list:
            if not monitoring_found:
                print("\nMONITORING:")
                monitoring_found = True
            print(f"  {monitor_type.upper()}: {', '.join(monitor_list)}")
    
    # Print errors if any
    if results.get("errors"):
        print("\nERRORS DURING ANALYSIS:")
        for error in results["errors"][:5]:  # Show first 5 errors
            print(f"  - {error}")
    
    print("\n" + "="*60)
    
    return 0

if __name__ == "__main__":
    exit(main())