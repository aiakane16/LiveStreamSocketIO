import React, { Component } from 'react';
import { Button, Text, View, DrawerLayoutAndroid } from 'react-native';

export default class HomeScreen extends Component {

  static navigationOptions = {
    title: 'Welcome',
  };

  render() {
    const {navigate} = this.props.navigation;

    var navigationView = (
      <View style={{flex: 1, backgroundColor: '#fff'}}>
        <Button
          title="Gallery"
          onPress={() => navigate('Profile', {name: 'Jane'})}
        />
      </View>
    );

    return (
      <DrawerLayoutAndroid
        drawerWidth={300}
        drawerPosition={DrawerLayoutAndroid.positions.Left}
        renderNavigationView={() => navigationView}>
       
        <View style={{flex: 1, alignItems: 'center'}}>
          <Text style={{margin: 10, fontSize: 15, textAlign: 'right'}}>World!</Text>
        </View>
      </DrawerLayoutAndroid>
    );
  }
}