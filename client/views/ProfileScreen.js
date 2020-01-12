import React, { Component } from 'react';
import { Button, Text, View, DrawerLayoutAndroid } from 'react-native';

export default class ProfileScreen extends Component {
    static navigationOptions = {
      title: 'Welcome',
    };
  
    render() {
      const {navigate} = this.props.navigation;
      
      return (
        <Button
          title="Jane's profile"
          onPress={() => navigate('Home', {name: 'Jane'})}
        />
      );
    }
  }