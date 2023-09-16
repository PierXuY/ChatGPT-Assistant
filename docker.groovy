parameters {
    string(
            description: '输入版本号',
            name: 'version',
            defaultValue: '1.0'
    )
}

def version = "${params.version}"

node {
    stage('git chekout') {
        git branch: 'main',
                url: 'https://github.com/fastjrun-ml/ChatGPT-Assistant.git'
    }
    stage('dockerFile') {
        sh 'rm -rf code && mkdir code'
        sh 'cp *.py ./code && cp Dockerfile ./code && cp requirements.txt ./code && cp *.sh ./code'
        sh 'cp -r ./text_toolkit ./voice_toolkit ./.streamlit ./code'
        dir('code'){
            stash 'code'
        }
    }
    stage('parallel docker build') {
        parallel (
                'docker build && push arm64': {
                    node('arm64') {
                        dir('workdir'){
                            unstash 'code'
                        }
                        sh 'cd workdir && docker build . -t pi4k8s/chatgpt-ai:$version-arm64'
                        sh 'docker push pi4k8s/chatgpt-ai:$version-arm64'
                    }
                },
                'docker build && push amd64': {
                    node('amd64') {
                        dir('workdir'){
                            unstash 'code'
                        }
                        sh 'cd workdir && docker build . -t pi4k8s/chatgpt-ai:$version-amd64'
                        sh 'docker push pi4k8s/chatgpt-ai:$version-amd64'
                    }
                }
        )
    }
    stage('manifest'){
        try {
            sh "docker manifest rm pi4k8s/chatgpt-ai:$version"
        }catch(exc){
            echo "some thing wrong"
        }
        sh "docker manifest create pi4k8s/chatgpt-ai:$version pi4k8s/chatgpt-ai:$version-amd64 pi4k8s/chatgpt-ai:$version-arm64"
        sh "docker manifest annotate pi4k8s/chatgpt-ai:$version pi4k8s/chatgpt-ai:$version-amd64 --os linux --arch amd64"
        sh "docker manifest annotate pi4k8s/chatgpt-ai:$version pi4k8s/chatgpt-ai:$version-arm64 --os linux --arch arm64"
        sh "docker manifest push pi4k8s/chatgpt-ai:$version"
    }
}