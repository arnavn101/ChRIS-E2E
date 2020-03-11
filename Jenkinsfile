pipeline {
	agent any
	triggers {
		cron('*/14400 * * * *')
	}
	stages {
		stage('test') {
			steps {
				sh '''
					python3 -u moc-health-check/automate.py
				'''
			}

			post {
				always{
					load "env.groovy"
					sh '''
						echo "Downloading build console output"
						cat ${JENKINS_HOME}/jobs/${JOB_NAME}/builds/${BUILD_NUMBER}/log >> log.txt
						ls -la
					'''
				}
					
				success{
					
					echo "------------------------ Build pass -----------------------------------------"
					emailext attachmentsPattern: 'log.txt', 
					body: "Pipeline: ${currentBuild.fullDisplayName} was successful",
					subject: "Build: ${currentBuild.fullDisplayName} passed", 
					to: "${env.TO}"
				}
				failure {
					echo "------------------------- Build failed --------------------------------------"
					emailext attachmentsPattern: 'log.txt', 
					body: "Something is wrong with pipeline: ${currentBuild.fullDisplayName}",
					subject: "Failed Pipeline: ${currentBuild.fullDisplayName}", 
					to: "${env.TO}"
					
				}
			}
		}
	}
}