import React, { Component } from 'react';
import CameraView from './views/CameraView';
import ImageView from './views/ImageView';
// import ProcessImageView from './views/ProcessImageView';
import {createAppContainer} from 'react-navigation';
import {createStackNavigator} from 'react-navigation-stack';

const MainNavigator = createStackNavigator({
  Capture: {screen: CameraView},
  ImageView : { screen: ImageView},
  // ProcessImageView : { screen: ProcessImageView}
});

const App = createAppContainer(MainNavigator);

export default App;

// export default class App extends Component {
//   render() {
//       return (
//           <CameraView />
//       );
//   };
// };
