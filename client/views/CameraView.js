import React, { Component, Fragment } from 'react';
import { View, Text } from 'react-native';
import * as Permissions from 'expo-permissions';
import { Camera } from 'expo-camera';
import Toolbar from '../components/toolbar';
import Gallery from '../components/gallery';
import styles from '../styles';

export default class CameraView extends Component {
    camera = null;
    state = {
        captures: [],
        // setting flash to be turned off by default
        flashMode: Camera.Constants.FlashMode.off,
        capturing: null,
        // start the back camera by default
        cameraType: Camera.Constants.Type.back,
        hasCameraPermission: null,
    };

    setFlashMode = (flashMode) => this.setState({ flashMode });
    setCameraType = (cameraType) => this.setState({ cameraType });
    handleCaptureIn = () => this.setState({ capturing: true });

    handleCaptureOut = () => {
        if (this.state.capturing)
            this.camera.stopRecording();
    };

    handleShortCapture = async () => {
        const photoData = await this.camera.takePictureAsync();
        this.setState({ capturing: false, captures: [photoData, ...this.state.captures] })
    };

    handleLongCapture = async () => {
        const videoData = await this.camera.recordAsync();

        this.setState({ capturing: false, captures: [videoData, ...this.state.captures] });
    };

    handlePhotoUpload = (photo) => {
        console.log('photo upload trigger')

        const {navigate} = this.props.navigation;
        const data = new FormData();
    
        data.append("image", {
            uri: photo.uri,
            name: 'sample',
            type: 'image/jpg'
        });
          
        fetch("https://8000-e30b46dc-4e8b-4cff-a247-c50875616ecd.ws-ap01.gitpod.io/predict", {
            method: "POST",
            body: data,
          })
            .then(response => {
              navigate('ImageView', { imageURI: photo.uri })

            })
            .catch(error => {
              console.log("upload error", error);
              alert("Upload failed!");
            //   navigate('ImageView',{ imageURI: photo.uri })
            });
    };

    async componentDidMount() {
        const camera = await Permissions.askAsync(Permissions.CAMERA);
        const audio = await Permissions.askAsync(Permissions.AUDIO_RECORDING);
        const hasCameraPermission = (camera.status === 'granted' && audio.status === 'granted');

        this.setState({ hasCameraPermission });
    };

    render() {
        const { hasCameraPermission, flashMode, cameraType, capturing, captures } = this.state;

        if (hasCameraPermission === null) {
            return <View />;
        } else if (hasCameraPermission === false) {
            return <Text>Access to camera has been denied.</Text>;
        }

        return (
            <Fragment>
                 <View  style={{ flex: 1 }}>
                    <Camera
                        type={cameraType}
                        flashMode={flashMode}
                        style={styles.preview}
                        ref={camera => this.camera = camera}
                    />
                </View>
                {captures.length > 0 && <Gallery 
                    handlePhotoUpload={this.handlePhotoUpload} 
                    captures={captures}
                />}
                <Toolbar 
                    capturing={capturing}
                    flashMode={flashMode}
                    cameraType={cameraType}
                    setFlashMode={this.setFlashMode}
                    setCameraType={this.setCameraType}
                    onCaptureIn={this.handleCaptureIn}
                    onCaptureOut={this.handleCaptureOut}
                    onLongCapture={this.handleLongCapture}
                    onShortCapture={this.handleShortCapture}
                />
            </Fragment>
            
        );
    };
};