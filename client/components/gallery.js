import React from 'react';
import { View, Image, ScrollView, TouchableOpacity } from 'react-native';

import styles from '../styles';

export default ({captures=[], handlePhotoUpload }) => (
    <ScrollView 
        horizontal={true}
        style={[styles.bottomToolbar, styles.galleryContainer]} 
    >
        {captures.map((photo) => (
            <View style={styles.galleryImageContainer} key={photo.uri}>
                <TouchableOpacity
                    onPress={()=> handlePhotoUpload(photo)}    
                >
                    <Image source={{ uri: photo.uri }} style={styles.galleryImage} />
                </TouchableOpacity>
            </View>
        ))}
    </ScrollView>
);