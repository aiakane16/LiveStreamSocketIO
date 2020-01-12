import React, { Component } from 'react'
import { View, Image, Text } from 'react-native'
import styles from '../styles'

export default class ProcessImageView extends Component {
    static navigationOptions = {
        title: 'Image View',
    };

    render(){
        var { imageURI } = this.props.navigation.state.params
        return (
            <View>
                <Image source={{ uri: imageURI}} style={styles.imageView} />
            </View>
        )
    }
}   